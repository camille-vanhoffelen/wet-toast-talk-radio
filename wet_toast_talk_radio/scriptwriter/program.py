import asyncio
from datetime import timedelta

import structlog
from langchain.base_language import BaseLanguageModel

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_offset_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue import MessageQueue
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebateShow

logger = structlog.get_logger()


class DailyProgram:
    program: tuple[RadioShow] = (TheGreatDebateShow, TheGreatDebateShow)

    def __init__(
        self,
        llm: BaseLanguageModel,
        media_store: MediaStore,
        message_queue: MessageQueue,
    ):
        self._media_store = media_store
        self._message_queue = message_queue
        self.program_iso_utc_date = get_offset_iso_utc_date(timedelta(days=2))
        self._shows = [
            show.create(llm=llm, media_store=media_store) for show in self.program
        ]
        self._warn_overwrite()
        logger.info(
            "Initialised daily program",
            date=self.program_iso_utc_date,
            program=self.program,
        )

    async def awrite(self):
        logger.info("Writing daily program...")
        tasks = []
        # TODO more elegant way to do this
        show_ids = []
        for i, show in enumerate(self._shows):
            show_id = ShowId(show_i=i, date=self.program_iso_utc_date)
            tasks.append(asyncio.create_task(show.awrite(show_id=show_id)))
            show_ids.append(show_id)
        await asyncio.gather(*tasks)
        # TODO failure handling, what if show fails to write? Can't send to queue
        self._message_queue.add_script_shows(shows=show_ids)

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
