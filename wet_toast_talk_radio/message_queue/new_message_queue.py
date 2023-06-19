import structlog

from wet_toast_talk_radio.message_queue.config import (
    StreamMQConfig,
    validate_config,
)
from wet_toast_talk_radio.message_queue.message_queue import StreamMessageQueue
from wet_toast_talk_radio.message_queue.sqs.message_queue import SQSStreamMessageQueue
from wet_toast_talk_radio.message_queue.virtual.message_queue import VirtualStreamMessageQueue

logger = structlog.get_logger()


def new_stream_message_queue(cfg: StreamMQConfig) -> StreamMessageQueue:
    validate_config(cfg)
    logger.debug("Creating new stream message queue", cfg=cfg)

    if cfg.virtual:
        return VirtualStreamMessageQueue()

    return SQSStreamMessageQueue(cfg.sqs)
