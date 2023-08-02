from guidance.llms import LLM

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow


class TheExpertZone(RadioShow):
    async def awrite(self, show_id: ShowId) -> bool:
        pass

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "RadioShow":
        pass
