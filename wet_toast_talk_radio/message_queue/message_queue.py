from abc import ABC, abstractmethod
from dataclasses import dataclass

from wet_toast_talk_radio.media_store.media_store import ShowId


@dataclass
class StreamShowMessage:
    show_id: ShowId
    receipt_handle: str


@dataclass
class ScriptShowMessage:
    show_id: ShowId
    receipt_handle: str


class MessageQueue(ABC):
    """Interface class to interact with the message queue"""

    # Stream shows #
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
    def purge_stream_shows(self):
        """Delete stream shows from the queue, effectively resetting the playlist."""

    # Script shows #
    @abstractmethod
    def poll_script_show(self) -> ScriptShowMessage | None:
        """Polls script show queue. This method is blocking.
        You should call delete_script_show after processing the message"""

    @abstractmethod
    def delete_script_show(self, _receipt_handle: str):
        """Delete the script show message from the queue.
        This is needed to prevent the message from being reprocessed"""

    @abstractmethod
    def add_script_shows(self, shows: list[ShowId]):
        """Add script shows to the queue"""

    @abstractmethod
    def purge_script_shows(self):
        """Delete script shows from the queue, effectively resetting the daily list to generate audio for."""

    @abstractmethod
    def change_message_visibility_timeout(self, receipt_handle: str, timeout_in_s: int):
        """Change the visibility timeout of a message
        Allows to implement a heartbeat to keep the message from being reprocessed, see:
        https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
        """
