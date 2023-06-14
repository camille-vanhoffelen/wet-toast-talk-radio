import multiprocessing
import time
from datetime import timedelta

import pytest

from wet_toast_talk_radio.common.aws_clients import new_s3_client, new_sqs_client
from wet_toast_talk_radio.disc_jockey.shout_client import _prepare
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.media_store.s3.config import S3Config
from wet_toast_talk_radio.message_queue.config import MessageQueueConfig
from wet_toast_talk_radio.message_queue.message_queue import StreamShowMessage
from wet_toast_talk_radio.message_queue.new_message_queue import new_message_queue
from wet_toast_talk_radio.message_queue.sqs.config import SQSConfig

_BUCKET_NAME = "wet-toast-talk-radio"

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


class TestStream:
    @pytest.mark.integration()
    def test_prepare(self, _clear_bucket, _clear_sqs):  # noqa: PT019
        media_store = new_media_store(
            MediaStoreConfig(s3=S3Config(bucket_name=_BUCKET_NAME, local=True))
        )
        message_queue = new_message_queue(
            MessageQueueConfig(
                sqs=SQSConfig(local=True, receive_message_blocking_time=0.1)
            )
        )
        today = get_current_iso_utc_date()

        show0 = ShowId(0, today)
        show1 = ShowId(1, today)
        media_store.put_transcoded_show(show0, b"foo0")
        media_store.put_transcoded_show(show1, b"foo1")

        stream_queue = multiprocessing.Queue(maxsize=1)

        prepare_process = multiprocessing.Process(
            target=_prepare,
            args=(message_queue, media_store, stream_queue, timedelta(microseconds=1)),
        )
        prepare_process.start()
        assert stream_queue.empty()

        message_queue.add_stream_shows(
            [
                StreamShowMessage(show0, "receipt_handle"),
                StreamShowMessage(show1, "receipt_handle"),
            ]
        )
        time.sleep(2)

        assert stream_queue.full()
        assert stream_queue.get() == (b"foo0", show0)
        assert stream_queue.get() == (b"foo1", show1)

        prepare_process.kill()
