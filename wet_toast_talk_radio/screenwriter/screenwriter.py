import structlog

from wet_toast_talk_radio.screenwriter.config import ScreenwriterConfig

logger = structlog.get_logger()


class Screenwriter:
    """Generate audio from text"""

    def __init__(self, cfg: ScreenwriterConfig):
        self._cfg = cfg

    def run(self) -> None:
        logger.warning("Not yet implemented")
        pass