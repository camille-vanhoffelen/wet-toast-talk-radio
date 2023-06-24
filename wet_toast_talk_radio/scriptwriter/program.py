import asyncio
from datetime import timedelta

import structlog
from langchain.base_language import BaseLanguageModel

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_offset_iso_utc_date
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebateShow

logger = structlog.get_logger()


class DailyProgram:
    program: tuple[RadioShow] = (TheGreatDebateShow, TheGreatDebateShow)

    def __init__(self, llm: BaseLanguageModel, media_store: MediaStore):
        self.program_iso_utc_date = get_offset_iso_utc_date(timedelta(days=2))
        self._shows = [
            show.create(llm=llm, media_store=media_store) for show in self.program
        ]
        # TODO defensive programing to check if scripts not already written for show date?
        logger.info(
            "Initialised daily program",
            date=self.program_iso_utc_date,
            program=self.program,
        )

    async def awrite(self):
        logger.info("Writing daily program...")
        tasks = []
        for i, show in enumerate(self._shows):
            tasks.append(
                asyncio.create_task(
                    show.awrite(show_i=i, show_iso_utc_date=self.program_iso_utc_date)
                )
            )
        await asyncio.gather(*tasks)
