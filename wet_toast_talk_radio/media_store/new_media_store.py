import structlog

from wet_toast_talk_radio.media_store.config import MediaStoreConfig, validate_config
from wet_toast_talk_radio.media_store.media_store import MediaStore
from wet_toast_talk_radio.media_store.s3.media_store import S3MediaStore
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore

logger = structlog.get_logger()


def new_media_store(cfg: MediaStoreConfig) -> MediaStore:
    """Return a new media store instance"""
    validate_config(cfg)
    logger.debug("Creating new media store", cfg=cfg)

    if cfg.virtual:
        return VirtualMediaStore()

    return S3MediaStore(cfg.s3)
