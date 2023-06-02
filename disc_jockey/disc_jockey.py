from disc_jockey import DiscJockeyConfig
import structlog


logger = structlog.get_logger()


class DiscJockey:
    """DiscJockey is responsible for transcoding media files to mp3 and uploading them to the media stream server"""

    def __init__(self, cfg: DiscJockeyConfig):
        self._cfg = cfg

    def run(self) -> None:
        """Run disc_jockey"""
        logger.info("Mixing the music.....")
