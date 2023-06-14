from pydantic import BaseModel

from wet_toast_talk_radio.message_queue.sqs.config import SQSConfig


class MessageQueueConfig(BaseModel):
    virtual: bool = False
    sqs: SQSConfig | None = None


def validate_config(cfg: MessageQueueConfig):
    assert cfg is not None, "MessageQueueConfig is none"
    if not cfg.sqs:
        assert (
            cfg.virtual
        ), "If message_queue.sqs is not set, then message_queue.virtual must be set"
