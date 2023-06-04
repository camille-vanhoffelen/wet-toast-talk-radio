from pydantic import BaseModel


class MediaStoreConfig(BaseModel):
    virtual: bool = False


def validate_config(cfg: MediaStoreConfig):
    assert cfg is not None, "MediaStoreConfig"
