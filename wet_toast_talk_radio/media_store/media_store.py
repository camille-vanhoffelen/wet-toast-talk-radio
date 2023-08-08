from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from wet_toast_talk_radio.common.dialogue import Line

_FALLBACK_KEY = "fallback"


@dataclass
class ShowId:
    show_i: int
    date: str

    def store_key(self):
        return f"{self.date}/{self.show_i}"


class ShowName(Enum):
    THE_GREAT_DEBATE = "the_great_debate"
    THE_EXPERT_ZONE = "the_expert_zone"
    MODERN_MINDFULNESS = "modern_mindfulness"
    ADVERTS = "adverts"
    PROLOVE = "prolove"


@dataclass
class ShowMetadata:
    show_name: ShowName


def show_id_from_raw_key(key: str) -> ShowId:
    return ShowId(
        show_i=int(key.split("/")[1]),
        date=key.split("/")[0],
    )


@dataclass
class ShowUploadInput:
    show_id: ShowId
    path: Path


class MediaStore(ABC):
    """Interface class to interact with the media store

    The media store should follow the following structure:

    - raw/<iso-date>/<incremental-int-show-id>/show.wav
    - transcoded/<iso-date>/<incremental-int-show-id>/show.mp3
    - scripts/<iso-date>/<incremental-int-show-id>/show.jsonl

    A show id is '<iso-date>/<incremental-int-show-id>'
    """

    @abstractmethod
    def put_raw_show(self, show_id: ShowId, data: bytes):
        """Upload raw show (.wav) to the media store"""

    @abstractmethod
    def put_transcoded_show(self, show_id: ShowId, data: bytes):
        """Put show (.mp3) to the media store"""

    @abstractmethod
    def put_script_show(self, show_id: ShowId, lines: list[Line]):
        """Put script (.jsonl) to the media store"""

    @abstractmethod
    def put_script_show_metadata(self, show_id: ShowId, metadata: ShowMetadata):
        """Put script metadata (.json) to the media store"""

    @abstractmethod
    def upload_transcoded_shows(self, shows: list[ShowUploadInput]):
        """Upload shows (.mp3) to the media store concurently"""

    @abstractmethod
    def download_raw_shows(self, show_ids: list[ShowId], dir_output: Path):
        """download raw shows (.wav) from the media store concurently"""

    @abstractmethod
    def download_script_show(self, show_id: ShowId, dir_output: Path):
        """download script (.jsonl) from the media store"""

    @abstractmethod
    def download_script_show_metadata(self, show_id: ShowId, dir_output: Path):
        """download script metadata(.json) from the media store"""

    @abstractmethod
    def get_transcoded_show(self, show_id: ShowId) -> bytes:
        """get transcoded show (.mp3) from the media store"""

    @abstractmethod
    def list_raw_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        """list raw shows ids from the media store"""

    @abstractmethod
    def list_transcoded_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        """list transcoded shows ids from the media store"""

    @abstractmethod
    def list_fallback_transcoded_shows(self) -> list[ShowId]:
        """list fallback transcoded shows ids from the media store"""

    @abstractmethod
    def list_script_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        """list scripts names from the media store"""
