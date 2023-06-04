from media_store.config import MediaStoreConfig
from media_store.media_store import MediaStore
from media_store.s3 import S3MediaStore
from media_store.virtual import VirtualMediaStore


def new_media_store(cfg: MediaStoreConfig) -> MediaStore:
    """Return a new media store instance"""

    if cfg.virtual:
        return VirtualMediaStore()


__all__ = [
    "MediaStore",
    "S3MediaStore",
    "VirtualMediaStore",
    "MediaStoreConfig",
    "new_media_store",
]
