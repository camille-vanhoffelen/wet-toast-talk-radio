import time
from pathlib import Path

import structlog

from tests.conftests import _BUCKET_NAME, _QUEUE_NAME
from wet_toast_talk_radio.common.aws_clients import new_s3_client, new_sqs_client
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import _FALLBACK_KEY, ShowId
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.media_store.s3.config import S3Config

logger = structlog.get_logger()


def clear_bucket():
    s3_client = new_s3_client(local=True)
    response = s3_client.list_objects_v2(Bucket=_BUCKET_NAME)
    if "Contents" in response:
        objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]
        response = s3_client.delete_objects(
            Bucket=_BUCKET_NAME, Delete={"Objects": objects_to_delete}
        )


def clear_sqs():
    sqs_client = new_sqs_client(local=True)
    queue_url = sqs_client.get_queue_url(QueueName=_QUEUE_NAME)["QueueUrl"]
    sqs_client.purge_queue(QueueUrl=queue_url)
    while True:
        response = sqs_client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )
        message_count = int(response["Attributes"]["ApproximateNumberOfMessages"])

        if message_count == 0:
            break

        time.sleep(1)


if __name__ == "__main__":
    clear_bucket()
    clear_sqs()
    media_store = new_media_store(
        MediaStoreConfig(s3=S3Config(bucket_name=_BUCKET_NAME, local=True))
    )

    data_dir = Path(__file__).parent
    today = get_current_iso_utc_date()
    raw_i = 0
    fallback_i = 0
    for file in data_dir.iterdir():
        if file.is_file() and file.name.endswith(".wav"):
            show = ShowId(raw_i, today)
            logger.info("Loading raw show", show=show)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_raw_show(show, data)
            raw_i += 1

        if file.is_file() and file.name.endswith(".ogg"):
            show = ShowId(fallback_i, _FALLBACK_KEY)
            logger.info("Loading fallback show", show=show)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_transcoded_show(show, data)
            fallback_i += 1
