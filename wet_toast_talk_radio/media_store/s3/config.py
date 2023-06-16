from pydantic import BaseModel


class S3Config(BaseModel):
    # This will connect to localstack at `http://localhost:4566`
    local: bool = False

    bucket_name: str | None = "media-store"
    max_workers: int = 10


def validate_config(cfg: S3Config):
    assert cfg is not None, "S3Config is none"
    assert cfg.bucket_name, "media_store.s3.bucket_name is not set"
