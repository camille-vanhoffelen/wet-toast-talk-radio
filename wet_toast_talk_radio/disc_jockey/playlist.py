from pydantic import BaseModel

from wet_toast_talk_radio.media_store.media_store import MediaStore
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue


class ShoutClientConfig(BaseModel):
    pass


class Playlist:
    def __init__(self, media_store: MediaStore, message_queue: MessageQueue) -> None:
        self._media_store = media_store
        self._message_queue = message_queue

    def start(self):
        # Get transcoded shows from today in media store
        # if no today folder, then use "fallback" folder
        # Upload shows to message queue
        pass
