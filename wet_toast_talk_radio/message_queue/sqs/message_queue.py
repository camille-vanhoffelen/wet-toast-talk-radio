import dataclasses
import json
import time
from datetime import datetime, timedelta

import structlog

from wet_toast_talk_radio.common.aws_clients import new_sqs_client
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue.message_queue import (
    MessageQueue,
    ScriptShowMessage,
    StreamShowMessage,
)
from wet_toast_talk_radio.message_queue.sqs.config import (
    SQSConfig,
    validate_config,
)

logger = structlog.get_logger()


class SQSMessageQueue(MessageQueue):
    def __init__(self, cfg: SQSConfig):
        validate_config(cfg)
        self._cfg = cfg
        stream_resp = new_sqs_client(self._cfg.local).get_queue_url(
            QueueName=cfg.stream_queue_name
        )
        self._stream_queue_url = stream_resp["QueueUrl"]
        script_resp = new_sqs_client(self._cfg.local).get_queue_url(
            QueueName=cfg.script_queue_name
        )
        self._script_queue_url = script_resp["QueueUrl"]

    def get_next_stream_show(self) -> StreamShowMessage:
        while True:
            response = new_sqs_client(self._cfg.local).receive_message(
                QueueUrl=self._stream_queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=self._cfg.receive_message_wait_time_in_s,
            )
            if _has_message(response):
                return _response_to_stream_show_message(response)

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

    def poll_script_show(self) -> ScriptShowMessage | None:
        logger.info("Polling script show")
        response = new_sqs_client(self._cfg.local).receive_message(
            QueueUrl=self._script_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=self._cfg.receive_message_wait_time_in_s,
        )
        if _has_message(response):
            return _response_to_script_show_message(response)
        else:
            return None

    def delete_script_show(self, receipt_handle: str):
        new_sqs_client(self._cfg.local).delete_message(
            QueueUrl=self._script_queue_url, ReceiptHandle=receipt_handle
        )

    def add_script_shows(self, shows: list[ShowId]):
        logger.info("Adding script shows to MQ", shows=shows)
        for show in shows:
            show_id_json = json.dumps(dataclasses.asdict(show))
            new_sqs_client(self._cfg.local).send_message(
                QueueUrl=self._script_queue_url,
                MessageBody=show_id_json,
                MessageGroupId="script_shows",
            )

    def change_message_visibility_timeout(self, receipt_handle: str, timeout_in_s: int):
        logger.debug(
            "Changing message visibility timeout",
            receipt_handle=receipt_handle,
            timeout_in_s=timeout_in_s,
        )
        new_sqs_client(self._cfg.local).change_message_visibility(
            QueueUrl=self._script_queue_url,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=timeout_in_s,
        )


def _has_message(response: dict) -> bool:
    return "Messages" in response and len(response["Messages"]) > 0


def _response_to_script_show_message(response: dict) -> ScriptShowMessage:
    msg = response["Messages"][0]
    show_id_dict = json.loads(msg["Body"])
    return ScriptShowMessage(
        show_id=ShowId(**show_id_dict),
        receipt_handle=msg["ReceiptHandle"],
    )


def _response_to_stream_show_message(response: dict) -> StreamShowMessage:
    msg = response["Messages"][0]
    show_id_dict = json.loads(msg["Body"])
    return StreamShowMessage(
        show_id=ShowId(**show_id_dict),
        receipt_handle=msg["ReceiptHandle"],
    )
