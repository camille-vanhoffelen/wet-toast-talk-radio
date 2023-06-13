from abc import ABC, abstractmethod
from dataclasses import dataclass

from wet_toast_talk_radio.media_store.media_store import ShowId


@dataclass
class StreamShowMessage:
    show_id: ShowId
    receipt_handle: str


class MessageQueue(ABC):
    """Interface class to interact with the message queue"""

    @abstractmethod
    def get_next_stream_show(self) -> StreamShowMessage:
        """Get the next stream show from the queue, this method should block until a message is available.
        You should call delete_stream_show when you are done processing the message"""

    @abstractmethod
    def delete_stream_show(self, _receipt_handle: str):
        """Delete the stream show message from the queue.
        This is needed to prevent the message from being reprocessed"""

    @abstractmethod
    def add_stream_shows(self, shows: list[StreamShowMessage]):
        """Add stream shows to the queue"""
