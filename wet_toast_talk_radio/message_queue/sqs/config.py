from pydantic import BaseModel, StrictInt


class SQSConfig(BaseModel):
    # This will connect to localstack at `http://localhost:4566`
    local: bool = False

    stream_queue_name: str = "stream-shows.fifo"
    script_queue_name: str = "script-shows.fifo"
    # AWS SDK only accepts ints, and don't want to silently cast 0.1 to 0
    receive_message_wait_time_in_s: StrictInt = 10


def validate_config(cfg: SQSConfig):
    assert cfg is not None, "SQSConfig is none"
