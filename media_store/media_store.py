from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


class MediaStore(ABC):
    """Interface class to interact with the media store"""

    @abstractmethod
    def upload_raw_show(self, show_name: str, data: bytes):
        """Upload raw show (.wav) to the media store"""

    @abstractmethod
    def upload_transcoded_show(self, show_name: str, data: bytes):
        """Upload show (.ogg) to the media store"""

    @abstractmethod
    def upload_transcoded_shows(self, shows: list[Path]):
        """Upload shows (.ogg) to the media store concurently"""

    @abstractmethod
    def download_raw_shows(self, show_names: str, dir_output: Path):
        """download raw shows (.wav) from the media store concurently"""

    @abstractmethod
    def list_raw_shows(self, since: datetime | None = None) -> list[str]:
        """list raw shows names from the media store"""

    @abstractmethod
    def list_transcoded_shows(self, since: datetime | None = None) -> list[str]:
        """list transcoded shows names from the media store"""
