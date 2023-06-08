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
    def upload_script_show(self, show_name: str, content: str):
        """Upload script (.txt) to the media store"""

    @abstractmethod
    def upload_transcoded_shows(self, show_paths: list[Path]):
        """Upload shows (.ogg) to the media store concurently"""

    @abstractmethod
    def download_raw_shows(self, show_names: list[str], dir_output: Path):
        """download raw shows (.wav) from the media store concurently"""

    @abstractmethod
    def download_script_show(self, show_name: str, dir_output: Path):
        """download script (.txt) from the media store concurently"""

    @abstractmethod
    def list_raw_shows(self, since: datetime | None = None) -> list[str]:
        """list raw shows names from the media store"""

    @abstractmethod
    def list_transcoded_shows(self, since: datetime | None = None) -> list[str]:
        """list transcoded shows names from the media store"""

    @abstractmethod
    def list_script_shows(self, since: datetime | None = None) -> list[str]:
        """list scripts names from the media store"""
