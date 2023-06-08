import structlog

from wet_toast_talk_radio.media_store.config import MediaStoreConfig, validate_config
from wet_toast_talk_radio.media_store.media_store import MediaStore
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.media_store.s3.media_store import S3MediaStore
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore

logger = structlog.get_logger()

__all__ = [
    "MediaStore",
    "S3MediaStore",
    "VirtualMediaStore",
    "MediaStoreConfig",
    "new_media_store",
    "validate_config",
]
