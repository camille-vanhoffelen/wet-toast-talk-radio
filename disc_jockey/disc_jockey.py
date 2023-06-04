import structlog

from disc_jockey.config import DiscJockeyConfig
from disc_jockey.media_transcoder import MediaTranscoder
from media_store import MediaStore

logger = structlog.get_logger()


class DiscJockey:
    """DiscJockey is responsible for transcoding media files to .ogg and uploading them to the media stream server"""

    def __init__(self, cfg: DiscJockeyConfig, media_store: MediaStore):
        self._cfg = cfg
        self._media_store = media_store
        self._media_transcoder = MediaTranscoder(cfg.media_converter, self._media_store)

    def stream(self) -> None:
        """Stream the transcoded music to the VosCast server"""
        logger.info("Streaming the music...")

    def transcode_latest_media(self):
        self._media_transcoder.start()
