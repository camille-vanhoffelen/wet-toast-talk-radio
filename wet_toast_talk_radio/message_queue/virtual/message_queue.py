import multiprocessing
from datetime import timedelta
from queue import Empty

from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.message_queue.message_queue import (
    ScriptMessage,
    ScriptMQ,
    StreamMQ,
    StreamShowMessage,
)


class VirtualStreamMQ(StreamMQ):
    def __init__(self):
        self._queue = multiprocessing.Queue()

    def get_next_stream_show(self) -> StreamShowMessage:
        show_id = self._queue.get(block=True)
        return StreamShowMessage(show_id, receipt_handle="foo")

    def delete_stream_show(self, _receipt_handle: str):
        # not needed for non concurent virtual message queue
        pass

    def add_stream_shows(self, shows: list[ShowId]):
        for show in shows:
            self._queue.put(show)

    def purge_stream_shows(self, _total_time: timedelta, _wait: timedelta):
        try:
            while True:
                self._queue.get_nowait()
        except Empty:
            return


class VirtualScriptMQ(ScriptMQ):
    def __init__(self):
        self._queue = multiprocessing.Queue()

    def get_next_script(self) -> ScriptMessage:
        show_id = self._queue.get(block=True)
        return ScriptMessage(show_id, receipt_handle="foo")

    def delete_script(self, _receipt_handle: str):
        # not needed for non concurent virtual message queue
        pass

    def add_scripts(self, shows: list[ShowId]):
        for show in shows:
            self._queue.put(show)
