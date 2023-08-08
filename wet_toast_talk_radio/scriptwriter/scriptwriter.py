import asyncio
from datetime import timedelta

import structlog

from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_offset_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue import MessageQueue
from wet_toast_talk_radio.scriptwriter import new_llm
from wet_toast_talk_radio.scriptwriter.adverts import Advert
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig, validate_config
from wet_toast_talk_radio.scriptwriter.modern_mindfulness import ModernMindfulness
from wet_toast_talk_radio.scriptwriter.prolove import Prolove
from wet_toast_talk_radio.scriptwriter.the_expert_zone import TheExpertZone
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebate

logger = structlog.get_logger()

DAILY_PROGRAM = (
    TheGreatDebate,
    ModernMindfulness,
    TheExpertZone,
    Prolove,
    Advert,
    TheGreatDebate,
    ModernMindfulness,
    TheExpertZone,
    Prolove,
    Advert,
    TheGreatDebate,
    ModernMindfulness,
    TheExpertZone,
    Prolove,
    Advert,
) * 20


@task_log_ctx("script_writer")
class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    def __init__(
        self,
        cfg: ScriptwriterConfig,
        media_store: MediaStore,
        message_queue: MessageQueue,
        program: tuple = DAILY_PROGRAM,
    ):
        logger.info("Initializing scriptwriter")
        self._cfg = cfg
        validate_config(cfg)
        self._llm = new_llm(cfg=cfg.llm)
        self._media_store = media_store
        self._message_queue = message_queue
        self._program = program
        self.program_iso_utc_date = get_offset_iso_utc_date(timedelta(days=2))
        self._shows = [
            show.create(llm=self._llm, media_store=media_store) for show in program
        ]
        self._warn_overwrite()
        logger.info(
            "Initialised daily program",
            date=self.program_iso_utc_date,
            shows=self._shows,
        )

    def run(self) -> None:
        logger.info("Starting scriptwriter...")
        assert (
            self._media_store is not None
        ), "MediaStore must be provided to run Scriptwriter"
        asyncio.run(self.awrite())
        logger.info("Scriptwriter finished, exiting")

    async def awrite(self):
        logger.info("Writing daily program...")
        tasks = []
        all_shows = []
        for i, show in enumerate(self._shows):
            show_id = ShowId(show_i=i, date=self.program_iso_utc_date)
            tasks.append(asyncio.create_task(show.awrite(show_id=show_id)))
            all_shows.append(show_id)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        script_shows = self._filter_failures(all_shows, results)
        success_rate = len(script_shows) / len(all_shows)
        logger.info(
            "Finished writing daily program",
            success_rate=success_rate,
            n_shows=len(script_shows),
        )

        self._message_queue.purge_script_shows()
        self._message_queue.add_script_shows(shows=script_shows)

    def _filter_failures(self, shows: list[ShowId], results: list) -> list[ShowId]:
        successful_shows = []
        for show_id, result in zip(shows, results, strict=True):
            if isinstance(result, Exception) or result is False:
                logger.error(
                    "Failed to write show",
                    show_id=show_id,
                    error=result,
                )
            else:
                successful_shows.append(show_id)
        return successful_shows

    def _warn_overwrite(self):
        previous_shows = self._media_store.list_script_shows(
            dates={self.program_iso_utc_date}
        )
        if previous_shows:
            logger.warning(
                "Overwriting previous shows",
                date=self.program_iso_utc_date,
                previous_shows=previous_shows,
            )
