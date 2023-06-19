import dataclasses
import json
import time
import uuid
from datetime import datetime, timedelta

from wet_toast_talk_radio.common.aws_clients import new_sqs_client
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue.message_queue import (
    StreamMessageQueue,
    StreamShowMessage,
)
from wet_toast_talk_radio.message_queue.sqs.config import (
    SQSConfig,
    validate_config,
)


class SQSStreamMessageQueue(StreamMessageQueue):
    def __init__(self, cfg: SQSConfig):
        validate_config(cfg)
        self._cfg = cfg
        resp = new_sqs_client(self._cfg.local).get_queue_url(
            QueueName=cfg.message_queue_name
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
                show_id_dict = json.loads(msg["Body"])
                return StreamShowMessage(
                    show_id=ShowId(**show_id_dict),
                    receipt_handle=msg["ReceiptHandle"],
                )

            time.sleep(self._cfg.receive_message_blocking_time)

    def delete_stream_show(self, receipt_handle: str):
        new_sqs_client(self._cfg.local).delete_message(
            QueueUrl=self._stream_queue_url, ReceiptHandle=receipt_handle
        )

    def add_stream_shows(self, shows: list[ShowId]):
        for show in shows:
            show_id_json = json.dumps(dataclasses.asdict(show))
            new_sqs_client(self._cfg.local).send_message(
                QueueUrl=self._stream_queue_url,
                MessageBody=show_id_json,
                MessageGroupId="stream_shows",
                MessageDeduplicationId=show.store_key() + "/" + str(uuid.uuid4()),
            )

    def purge_stream_shows(self, total_time: timedelta, wait: timedelta):
        sqs_client = new_sqs_client(self._cfg.local)
        sqs_client.purge_queue(QueueUrl=self._stream_queue_url)
        success = False
        end_time = datetime.now() + total_time
        while datetime.now() < end_time:
            response = sqs_client.get_queue_attributes(
                QueueUrl=self._stream_queue_url,
                AttributeNames=["ApproximateNumberOfMessages"],
            )
            message_count = int(response["Attributes"]["ApproximateNumberOfMessages"])

            if message_count == 0:
                success = True
                break

            time.sleep(wait.total_seconds())

        if not success:
            raise Exception(
                f"Unable to purge queue in time, total_time={total_time}, wait={wait}"
            )
