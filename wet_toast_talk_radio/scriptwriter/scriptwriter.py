import structlog

from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig

logger = structlog.get_logger()


class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    def __init__(self, cfg: ScriptwriterConfig):
        self._cfg = cfg

    def run(self) -> None:
        logger.warning("Not yet implemented")
        pass
