import asyncio

import structlog

from wet_toast_talk_radio.common.task_log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.scriptwriter import DailyProgram, new_llm
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig, validate_config

logger = structlog.get_logger()


@task_log_ctx("script_writer")
class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    def __init__(self, cfg: ScriptwriterConfig, media_store: MediaStore | None = None):
        logger.info("Initializing scriptwriter", cfg=cfg)
        self._cfg = cfg
        validate_config(cfg)
        self._llm = new_llm(cfg=cfg.llm)
        self._media_store = media_store

    def run(self) -> None:
        logger.info("Starting scriptwriter...")
        assert (
            self._media_store is not None
        ), "MediaStore must be provided to run Scriptwriter"
        daily_program = DailyProgram(llm=self._llm, media_store=self._media_store)
        asyncio.run(daily_program.awrite())
        logger.info("Scriptwriter finished, exiting")
