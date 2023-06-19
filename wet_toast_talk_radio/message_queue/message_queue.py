from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta

from wet_toast_talk_radio.media_store.media_store import ShowId


@dataclass
class StreamShowMessage:
    show_id: ShowId
    receipt_handle: str


class StreamMessageQueue(ABC):
    """Interface class to interact with the stream message queue"""

    @abstractmethod
    def get_next_stream_show(self) -> StreamShowMessage:
        """Get the next stream show from the queue, this method should block until a message is available.
        You should call delete_stream_show when you are done processing the message"""

    @abstractmethod
    def delete_stream_show(self, _receipt_handle: str):
        """Delete the stream show message from the queue.
        This is needed to prevent the message from being reprocessed"""

    @abstractmethod
    def add_stream_shows(self, shows: list[ShowId]):
        """Add stream shows to the queue"""

    @abstractmethod
    def purge_stream_shows(self, total_time: timedelta, wait: timedelta):
        """Delete stream shows from the queue, effectually reseting the playlist.
        total_time: The total time to wait for queue to be purged
        wait: The time to wait between each check to see if the queue is empty
        """


@dataclass
class ScriptMessage:
    show_id: ShowId
    receipt_handle: str


class ScriptMessageQueue(ABC):
    """Interface class to interact with the script message queue"""

    @abstractmethod
    def get_next_script(self) -> ScriptMessage:
        """Get the next script from the queue, this method should block until a message is available.
        You should call delete_script when you are done processing the message"""

    @abstractmethod
    def delete_script(self, _receipt_handle: str):
        """Delete the script message from the queue.
        This is needed to prevent the message from being reprocessed"""

    @abstractmethod
    def add_scripts(self, shows: list[ShowId]):
        """Add scripts to the queue"""