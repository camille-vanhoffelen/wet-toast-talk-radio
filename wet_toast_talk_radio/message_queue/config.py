from pydantic import BaseModel

from wet_toast_talk_radio.message_queue.sqs.config import SQSConfig


class StreamMQConfig(BaseModel):
    virtual: bool = False
    sqs: SQSConfig | None = None


class ScriptMQConfig(BaseModel):
    virtual: bool = False
    sqs: SQSConfig | None = None


def validate_stream_config(cfg: StreamMQConfig):
    assert cfg is not None, "StreamMQConfig is none"
    if not cfg.sqs:
        assert (
            cfg.virtual
        ), "If stream_message_queue.sqs is not set, then stream_message_queue.virtual must be set"


def validate_script_config(cfg: ScriptMQConfig):
    assert cfg is not None, "ScriptMQConfig is none"
    if not cfg.sqs:
        assert (
            cfg.virtual
        ), "If script_message_queue.sqs is not set, then script_message_queue.virtual must be set"
