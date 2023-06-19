from pydantic import BaseModel

from wet_toast_talk_radio.message_queue.sqs.config import SQSConfig


class StreamMQConfig(BaseModel):
    virtual: bool = False
    sqs: SQSConfig | None = None


def validate_config(cfg: StreamMQConfig):
    assert cfg is not None, "StreamMQConfig is none"
    if not cfg.sqs:
        assert (
            cfg.virtual
        ), "If stream_message_queue.sqs is not set, then stream_message_queue.virtual must be set"
