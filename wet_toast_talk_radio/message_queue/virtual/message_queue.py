import multiprocessing
from datetime import timedelta
from queue import Empty

from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue.message_queue import (
    MessageQueue,
    ScriptShowMessage,
    StreamShowMessage,
)


class VirtualMessageQueue(MessageQueue):
    def __init__(self):
        self._queues = {
            "stream": multiprocessing.Queue(),
            "script": multiprocessing.Queue(),
        }

    def get_next_stream_show(self) -> StreamShowMessage:
        show_id = self._queues["stream"].get(block=True)
        return StreamShowMessage(show_id, receipt_handle="foo")

    def delete_stream_show(self, _receipt_handle: str):
        # not needed for non concurrent virtual message queue
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

    def poll_script_show(self) -> ScriptShowMessage:
        show_id = self._queues["script"].get(block=True)
        return ScriptShowMessage(show_id, receipt_handle="foo")

    def delete_script_show(self, _receipt_handle: str):
        # not needed for non concurrent virtual message queue
        pass

    def add_script_shows(self, shows: list[ShowId]):
        for show in shows:
            self._queues["script"].put(show)

    def change_message_visibility_timeout(self, receipt_handle: str, timeout_in_s: int):
        # not needed for virtual message queue
        pass
