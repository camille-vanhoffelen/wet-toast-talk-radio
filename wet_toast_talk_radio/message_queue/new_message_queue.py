import structlog

from wet_toast_talk_radio.message_queue.config import (
    MessageQueueConfig,
    validate_config,
)
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue
from wet_toast_talk_radio.message_queue.sqs.message_queue import SQSMessageQueue
from wet_toast_talk_radio.message_queue.virtual.message_queue import VirtualMessageQueue

logger = structlog.get_logger()


def new_message_queue(cfg: MessageQueueConfig) -> MessageQueue:
    validate_config(cfg)
    logger.info("Creating new media store", cfg=cfg)

    if cfg.virtual:
        return VirtualMessageQueue()

    return SQSMessageQueue(cfg.sqs)
