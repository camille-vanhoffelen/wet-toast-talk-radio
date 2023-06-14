import multiprocessing
import time
from datetime import timedelta

import pytest

from wet_toast_talk_radio.common.aws_clients import new_s3_client, new_sqs_client
from wet_toast_talk_radio.disc_jockey.shout_client import _prepare
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
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

        media_store.upload_transcoded_show("show1.ogg", "foo1")
        media_store.upload_transcoded_show("show2.ogg", "foo2")

        stream_queue = multiprocessing.Queue(maxsize=1)

        prepare_process = multiprocessing.Process(
            target=_prepare,
            args=(message_queue, media_store, stream_queue, timedelta(microseconds=1)),
        )
        prepare_process.start()
        assert stream_queue.empty()

        message_queue.add_stream_shows(
            [
                StreamShowMessage("show1.ogg", "receipt_handle"),
                StreamShowMessage("show2.ogg", "receipt_handle"),
            ]
        )
        time.sleep(2)

        assert stream_queue.full()
        assert stream_queue.get() == (b"foo1", "show1.ogg")
        assert stream_queue.get() == (b"foo2", "show2.ogg")

        prepare_process.kill()
