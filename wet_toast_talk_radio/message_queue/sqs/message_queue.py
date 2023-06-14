import time
import uuid

from wet_toast_talk_radio.common.aws_clients import new_sqs_client
from wet_toast_talk_radio.message_queue.message_queue import (
    MessageQueue,
    StreamShowMessage,
)
from wet_toast_talk_radio.message_queue.sqs.config import (
    SQSConfig,
    validate_config,
)


class SQSMessageQueue(MessageQueue):
    def __init__(self, cfg: SQSConfig):
        validate_config(cfg)
        self._cfg = cfg
        resp = new_sqs_client(self._cfg.local).get_queue_url(
            QueueName=cfg.stream_queue_name
        )
        self._stream_queue_url = resp["QueueUrl"]

    def get_next_stream_show(self) -> StreamShowMessage:
        while True:
            response = new_sqs_client(self._cfg.local).receive_message(
                QueueUrl=self._stream_queue_url,
                MaxNumberOfMessages=1,
            )
            if "Messages" in response and len(response["Messages"]) > 0:
                msg = response["Messages"][0]
                return StreamShowMessage(
                    show_id=msg["Body"],
                    receipt_handle=msg["ReceiptHandle"],
                )

            time.sleep(self._cfg.receive_message_blocking_time)

    def delete_stream_show(self, receipt_handle: str):
        new_sqs_client(self._cfg.local).delete_message(
            QueueUrl=self._stream_queue_url, ReceiptHandle=receipt_handle
        )

    def add_stream_shows(self, shows: list[StreamShowMessage]):
        for show in shows:
            new_sqs_client(self._cfg.local).send_message(
                QueueUrl=self._stream_queue_url,
                MessageBody=show.show_id,
                MessageGroupId="stream_shows",
                MessageDeduplicationId=show.show_id + "-" + str(uuid.uuid4()),
            )
