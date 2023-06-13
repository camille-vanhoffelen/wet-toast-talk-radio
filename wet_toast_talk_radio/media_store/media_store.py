from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ShowId:
    show_i: int
    date: str

    def store_key(self):
        return f"{self.date}/{self.show_i}"


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
    - transcoded/<iso-date>/<incremental-int-show-id>/show.ogg
    - scripts/<iso-date>/<incremental-int-show-id>/show.txt

    A show id is '<iso-date>/<incremental-int-show-id>'
    """

    @abstractmethod
    def put_raw_show(self, show_id: ShowId, data: bytes):
        """Upload raw show (.wav) to the media store"""

    @abstractmethod
    def put_transcoded_show(self, show_id: ShowId, data: bytes):
        """Put show (.ogg) to the media store"""

    @abstractmethod
    def put_script_show(self, show_id: ShowId, content: str):
        """Put script (.txt) to the media store"""

    @abstractmethod
    def upload_transcoded_shows(self, shows: list[ShowUploadInput]):
        """Upload shows (.ogg) to the media store concurently"""

    @abstractmethod
    def download_raw_shows(self, show_ids: list[ShowId], dir_output: Path):
        """download raw shows (.wav) from the media store concurently"""

    @abstractmethod
    def download_script_show(self, show_id: ShowId, dir_output: Path):
        """download script (.txt) from the media store concurently"""

    @abstractmethod
    def get_transcoded_show(self, show_id: ShowId) -> bytes:
        """get transcoded show (.ogg) from the media store"""

    @abstractmethod
    def list_raw_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        """list raw shows ids from the media store"""

    @abstractmethod
    def list_transcoded_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        """list transcoded shows ids from the media store"""

    @abstractmethod
    def list_script_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        """list scripts names from the media store"""
