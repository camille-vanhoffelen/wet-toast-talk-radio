from abc import ABC, abstractmethod

from guidance.llms import LLM

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.common.log_ctx import show_id_log_ctx


class RadioShow(ABC):
    @classmethod
    @abstractmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "RadioShow":
        """Factory method"""

    @show_id_log_ctx()
    @abstractmethod
    async def awrite(self, show_id: ShowId) -> bool:
        """Asynchronously write the script for the show using an LLM.
        Script is stored in the media store under show_id.
        Returns true if successful, false otherwise"""
