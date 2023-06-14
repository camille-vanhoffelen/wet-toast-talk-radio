import multiprocessing
from datetime import timedelta
from queue import Empty

from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue.message_queue import (
    MessageQueue,
    StreamShowMessage,
)


class VirtualMessageQueue(MessageQueue):
    def __init__(self):
        self._queues = {"stream": multiprocessing.Queue()}

    def get_next_stream_show(self) -> StreamShowMessage:
        show_id = self._queues["stream"].get(block=True)
        return StreamShowMessage(show_id, receipt_handle="foo")

    def delete_stream_show(self, _receipt_handle: str):
        # not needed for non concurent virtual message queue
        pass

    def add_stream_shows(self, shows: list[ShowId]):
        for show in shows:
            self._queues["stream"].put(show)

    def purge_stream_shows(self, _total_time: timedelta, _wait: timedelta):
        try:
            while True:
                self._queues["stream"].get_nowait()
        except Empty:
            return
