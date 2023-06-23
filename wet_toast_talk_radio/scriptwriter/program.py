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
        self.shows = [
            # TODO turn Chain to Show, or use composition cause we don't want to run w/ args like topic! want them fetched from somewhere
            TheGreatDebateShow(llm=llm, media_store=media_store),
        ]
        logger.info("Initialized DailyProgram", shows=self.shows)

    async def awrite(self):
        tasks = []
        for show in self.shows:
            # TODO show ordering i.e show_i, since not guaranteed ordered execution
            tasks.append(asyncio.create_task(show.arun()))
        await asyncio.gather(*tasks)
