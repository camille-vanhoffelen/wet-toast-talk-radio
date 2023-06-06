import multiprocessing

from wet_toast_talk_radio.message_queue.message_queue import (
    MessageQueue,
    StreamShowMessage,
)


class VirtualMessageQueue(MessageQueue):
    def __init__(self):
        self._queues = {"stream": multiprocessing.Queue()}

    def get_next_stream_show(self) -> StreamShowMessage:
        return self._queues["stream"].get(block=True)

    def delete_stream_show(self, _receipt_handle: str):
        # not needed for non concurent virtual message queue
        pass

    def add_stream_shows(self, shows: list[StreamShowMessage]):
        for show in shows:
            self._queues["stream"].put(show)
