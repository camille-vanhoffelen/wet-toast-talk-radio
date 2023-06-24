import asyncio
from datetime import timedelta

import structlog
from langchain.base_language import BaseLanguageModel

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_offset_iso_utc_date
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebateShow

logger = structlog.get_logger()


class DailyProgram:
    # TODO async? but ordered?
    # https://stackoverflow.com/questions/54668701/asyncio-gather-scheduling-order-guarantee
    def __init__(self, llm: BaseLanguageModel, media_store: MediaStore):
        self._program = [TheGreatDebateShow]
        self._shows = [
            show.create(llm=llm, media_store=media_store) for show in self._program
        ]
        # TODO defensive programing to check if scripts not already written for show date?
        self._program_iso_utc_date = get_offset_iso_utc_date(timedelta(days=2))
        logger.info("Initialised daily program", date=self._program_iso_utc_date, program=self._program)

    async def awrite(self):
        logger.info("Writing daily program...")
        tasks = []
        for i, show in enumerate(self._shows):
            tasks.append(
                asyncio.create_task(show.awrite(show_i=i, show_iso_utc_date=self._program_iso_utc_date))
            )
        await asyncio.gather(*tasks)
