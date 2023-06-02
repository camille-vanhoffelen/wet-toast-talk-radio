from abc import ABC, abstractmethod


class MediaStore(ABC):
    """Interface class to interact with the media store"""

    @abstractmethod
    def upload_raw_show(self):
        """Upload raw show (.wav) to the media store"""

    @abstractmethod
    def download_raw_show(self):
        """Download raw show (.wav) from the media store"""
