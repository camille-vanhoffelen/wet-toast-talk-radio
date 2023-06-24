from abc import ABC, abstractmethod

from langchain.base_language import BaseLanguageModel

from wet_toast_talk_radio.media_store import MediaStore


class RadioShow(ABC):
    @classmethod
    @abstractmethod
    def create(cls, llm: BaseLanguageModel, media_store: MediaStore) -> "RadioShow":
        """Factory method"""

    @abstractmethod
    async def awrite(self, show_i: int, show_iso_utc_date: str):
        """Asynchronously write the script for the show using an LLM.
        Script is stored in the media store.
        Show id is show_i, streaming date of the show is show_iso_utc_date"""
