import time
from pathlib import Path

import pytest

from wet_toast_talk_radio.common.aws_clients import new_s3_client, new_sqs_client
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import (
    _FALLBACK_KEY,
    MediaStore,
    ShowId,
)
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.media_store.s3.config import S3Config
from wet_toast_talk_radio.message_queue.config import StreamMQConfig
from wet_toast_talk_radio.message_queue.message_queue import StreamMessageQueue
from wet_toast_talk_radio.message_queue.new_message_queue import new_stream_message_queue
from wet_toast_talk_radio.message_queue.sqs.config import SQSConfig

_BUCKET_NAME = "media-store"

_QUEUE_NAME = "stream-shows.fifo"


@pytest.fixture()
def _clear_bucket():
    s3_client = new_s3_client(local=True)
    response = s3_client.list_objects_v2(Bucket=_BUCKET_NAME)
    if "Contents" in response:
        objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]
        response = s3_client.delete_objects(
            Bucket=_BUCKET_NAME, Delete={"Objects": objects_to_delete}
        )


@pytest.fixture()
def setup_bucket(_clear_bucket) -> dict[str, list[ShowId]]:
    media_store = new_media_store(
        MediaStoreConfig(s3=S3Config(bucket_name=_BUCKET_NAME, local=True))
    )
    data_dir = (
        Path(__file__).parent.parent / "wet_toast_talk_radio" / "media_store" / "data"
    )
    today = get_current_iso_utc_date()
    ret = {"raw": [], "fallback": []}
    raw_i = 0
    fallback_i = 0
    for file in data_dir.iterdir():
        if file.is_file() and file.name.endswith(".wav"):
            show = ShowId(raw_i, today)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_raw_show(show, data)
            ret["raw"].append(show)
            raw_i += 1
        if file.is_file() and file.name.endswith(".ogg"):
            show = ShowId(fallback_i, _FALLBACK_KEY)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_transcoded_show(show, data)
            ret["fallback"].append(show)
            fallback_i += 1
    return ret


@pytest.fixture()
def _clear_sqs():
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


@pytest.fixture()
def media_store() -> MediaStore:
    return new_media_store(
        MediaStoreConfig(s3=S3Config(bucket_name=_BUCKET_NAME, local=True))
    )


@pytest.fixture()
def message_queue() -> StreamMessageQueue:
    return new_stream_message_queue(
        StreamMQConfig(sqs=SQSConfig(local=True, receive_message_blocking_time=0.1))
    )
