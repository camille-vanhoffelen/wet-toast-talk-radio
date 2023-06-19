import structlog

from wet_toast_talk_radio.message_queue.config import (
    ScriptMQConfig,
    StreamMQConfig,
    validate_script_config,
    validate_stream_config,
)
from wet_toast_talk_radio.message_queue.message_queue import ScriptMQ, StreamMQ
from wet_toast_talk_radio.message_queue.sqs.message_queue import (
    SQSScriptMQ,
    SQSStreamMQ,
)
from wet_toast_talk_radio.message_queue.virtual.message_queue import (
    VirtualScriptMQ,
    VirtualStreamMQ,
)

logger = structlog.get_logger()


def new_stream_message_queue(cfg: StreamMQConfig) -> StreamMQ:
    validate_stream_config(cfg)
    logger.debug("Creating new stream message queue", cfg=cfg)

    if cfg.virtual:
        return VirtualStreamMQ()

    return SQSStreamMQ(cfg.sqs)


def new_script_message_queue(cfg: ScriptMQConfig) -> ScriptMQ:
    validate_script_config(cfg)
    logger.debug("Creating new script message queue", cfg=cfg)

    if cfg.virtual:
        return VirtualScriptMQ()

    return SQSScriptMQ(cfg.sqs)
