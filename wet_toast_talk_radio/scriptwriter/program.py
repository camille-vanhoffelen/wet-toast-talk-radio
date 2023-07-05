import asyncio
from datetime import timedelta

import structlog
from guidance.llms import LLM

from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_offset_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue import MessageQueue
from wet_toast_talk_radio.scriptwriter.adverts import Advert
from wet_toast_talk_radio.scriptwriter.modern_mindfulness import ModernMindfulness
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebate

logger = structlog.get_logger()

DAILY_PROGRAM = (
    TheGreatDebate,
    ModernMindfulness,
    Advert,
    TheGreatDebate,
    ModernMindfulness,
    Advert,
    TheGreatDebate,
    ModernMindfulness,
    Advert,
    TheGreatDebate,
    ModernMindfulness,
    Advert,
) * 24


@task_log_ctx("daily_program")
class DailyProgram:
    def __init__(
        self,
        llm: LLM,
        media_store: MediaStore,
        message_queue: MessageQueue,
        program: tuple = DAILY_PROGRAM,
    ):
        self._media_store = media_store
        self._message_queue = message_queue
        self.program_iso_utc_date = get_offset_iso_utc_date(timedelta(days=2))
        self._shows = [
            show.create(llm=llm, media_store=media_store) for show in program
        ]
        self._warn_overwrite()
        logger.info(
            "Initialised daily program",
            date=self.program_iso_utc_date,
            shows=self._shows,
        )

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
