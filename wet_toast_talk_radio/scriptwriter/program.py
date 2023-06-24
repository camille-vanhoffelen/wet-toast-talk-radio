import asyncio

import structlog
from langchain.base_language import BaseLanguageModel

from wet_toast_talk_radio.media_store import MediaStore
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
        logger.info("Daily program", program=self._program)

    async def awrite(self):
        logger.info("Writing daily program...")
        tasks = []
        for show in self._shows:
            # TODO show ordering i.e show_i, since not guaranteed ordered execution
            tasks.append(asyncio.create_task(show.awrite()))
        await asyncio.gather(*tasks)
