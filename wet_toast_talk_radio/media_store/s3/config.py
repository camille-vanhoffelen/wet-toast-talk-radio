from pydantic import BaseModel


class S3Config(BaseModel):
    # When using docker-compose locally, this should be set to `http://localhost:4566`
    local_endpoint: str | None = None
    bucket_name: str | None = "wet-toast-talk-radio"
    max_workers: int = 10


def validate_config(cfg: S3Config):
    assert cfg is not None, "S3Config is none"
    assert cfg.bucket_name, "media_store.s3.bucket_name is not set"
