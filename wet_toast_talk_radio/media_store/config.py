from pydantic import BaseModel

from wet_toast_talk_radio.media_store.s3.config import S3Config


class MediaStoreConfig(BaseModel):
    virtual: bool = False
    s3: S3Config | None = None


def validate_config(cfg: MediaStoreConfig):
    assert cfg is not None, "MediaStoreConfig is none"
    if not cfg.s3:
        assert (
            cfg.virtual
        ), "If media_store.s3 is not set, then media_store.virtual must be set"
