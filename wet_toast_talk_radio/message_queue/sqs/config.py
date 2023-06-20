from pydantic import BaseModel


class SQSConfig(BaseModel):
    # This will connect to localstack at `http://localhost:4566`
    local: bool = False

    message_queue_name: str
    receive_message_blocking_time: int = 10


def validate_config(cfg: SQSConfig):
    assert cfg is not None, "SQSConfig is none"
    assert cfg.message_queue_name is not None, "SQSConfig.message_queue_name is none"
