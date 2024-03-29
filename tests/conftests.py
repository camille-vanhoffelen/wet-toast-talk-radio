import json
import re
import time
from pathlib import Path

import pytest
import structlog

from wet_toast_talk_radio.common.aws_clients import new_s3_client, new_sqs_client
from wet_toast_talk_radio.common.dialogue import read_lines
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import (
    _FALLBACK_KEY,
    MediaStore,
    ShowId,
    ShowMetadata,
)
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.media_store.s3.config import S3Config
from wet_toast_talk_radio.message_queue.config import MessageQueueConfig
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue
from wet_toast_talk_radio.message_queue.new_message_queue import new_message_queue
from wet_toast_talk_radio.message_queue.sqs.config import SQSConfig
from wet_toast_talk_radio.radio_operator.config import RadioOperatorConfig
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator

logger = structlog.get_logger()

_BUCKET_NAME = "media-store"

_STREAM_QUEUE_NAME = "stream-shows.fifo"
_SCRIPT_QUEUE_NAME = "script-shows.fifo"


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
    logger.debug("Setting up test bucket based on data dir", data_dir=data_dir)
    today = get_current_iso_utc_date()
    ret = {"raw": [], "fallback": [], "script": []}

    for file in data_dir.iterdir():
        if file.is_file() and file.suffix == ".wav":
            show_i = _parse_show_id(file.name)
            show = ShowId(show_i=show_i, date=today)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_raw_show(show, data)
            ret["raw"].append(show)
        if file.is_file() and file.suffix == ".mp3":
            show_i = _parse_show_id(file.name)
            show = ShowId(show_i=show_i, date=_FALLBACK_KEY)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_transcoded_show(show, data)
            ret["fallback"].append(show)
        if file.is_file() and file.suffix == ".jsonl":
            show_i = _parse_show_id(file.name)
            show = ShowId(show_i=show_i, date=today)
            lines = read_lines(file)
            media_store.put_script_show(show_id=show, lines=lines)
            ret["script"].append(show)
        if file.is_file() and file.suffix == ".json":
            show_i = _parse_show_id(file.name)
            show = ShowId(show_i=show_i, date=today)
            metadata_dict = json.loads(file.read_text())
            metadata = ShowMetadata(**metadata_dict)
            media_store.put_script_show_metadata(show_id=show, metadata=metadata)
            ret["script"].append(show)

    return ret


def _parse_show_id(filename: str) -> int:
    """Parse show id from filename in the format: show<show_id>.<ext>"""
    pattern = r"show(\d+)\.(ogg|jsonl|wav|mp3|json)"
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Could not parse show id from filename {filename}")


@pytest.fixture()
def _clear_sqs():
    sqs_client = new_sqs_client(local=True)
    _purge_mq(sqs_client, _STREAM_QUEUE_NAME)
    _purge_mq(sqs_client, _SCRIPT_QUEUE_NAME)


def _purge_mq(client, queue_name):
    queue_url = client.get_queue_url(QueueName=queue_name)["QueueUrl"]
    client.purge_queue(QueueUrl=queue_url)
    while True:
        response = client.get_queue_attributes(
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
def message_queue() -> MessageQueue:
    return new_message_queue(
        MessageQueueConfig(sqs=SQSConfig(local=True, receive_message_wait_time_in_s=1))
    )


@pytest.fixture()
def radio_operator() -> RadioOperator:
    radio_operator = RadioOperator(RadioOperatorConfig())
    return radio_operator
