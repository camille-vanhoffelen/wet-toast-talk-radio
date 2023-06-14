import structlog

from wet_toast_talk_radio.disc_jockey.config import DiscJockeyConfig, validate_config
from wet_toast_talk_radio.disc_jockey.media_transcoder import MediaTranscoder
from wet_toast_talk_radio.disc_jockey.shout_client import ShoutClient
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue

logger = structlog.get_logger()


class DiscJockey:
    """DiscJockey is responsible for transcoding media files to .ogg and uploading them to the media stream server"""

    def __init__(
        self,
        cfg: DiscJockeyConfig | None,
        media_store: MediaStore | None = None,
        message_queue: MessageQueue | None = None,
    ):
        validate_config(cfg)
        self._cfg = cfg
        self._media_store = media_store
        self._message_queue = message_queue

    def stream(self) -> None:
        """Stream the transcoded music to the VosCast server"""
        shout_client = ShoutClient(self._cfg.shout_client, self._media_store)
        shout_client.start()
        shout_client.join()

    def transcode_latest_media(self):
        """Transcode the latest media files to .ogg and upload them to the Media Store"""
        media_transcoder = MediaTranscoder(
            self._cfg.media_transcoder, self._media_store
        )
        media_transcoder.start()
