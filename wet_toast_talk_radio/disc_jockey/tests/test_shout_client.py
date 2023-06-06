import multiprocessing
import time
from datetime import timedelta
from multiprocessing.managers import BaseManager

import pytest

from wet_toast_talk_radio.disc_jockey.shout_client import _prepare
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore
from wet_toast_talk_radio.message_queue.message_queue import StreamShowMessage
from wet_toast_talk_radio.message_queue.virtual.message_queue import VirtualMessageQueue


class VirtualManager(BaseManager):
    pass


VirtualManager.register("MediaStore", VirtualMediaStore)
VirtualManager.register("MessageQueue", VirtualMessageQueue)


@pytest.fixture()
def virtual_manager() -> MediaStore:
    with VirtualManager() as manager:
        yield manager


class TestShoutTranscoder:
    def test_prepare(self, virtual_manager: VirtualManager):
        media_store = virtual_manager.MediaStore()
        message_queue = virtual_manager.MessageQueue()

        stream_queue = multiprocessing.Queue(maxsize=1)
        media_store.upload_transcoded_show("show.ogg", "foo")

        prepare_process = multiprocessing.Process(
            target=_prepare,
            args=(message_queue, media_store, stream_queue, timedelta(microseconds=1)),
        )
        prepare_process.start()
        assert stream_queue.empty()
        message_queue.add_stream_shows(
            [StreamShowMessage("show.ogg", "receipt_handle")]
        )
        time.sleep(1)
        assert stream_queue.full()
        assert stream_queue.get() == ("foo", "show.ogg")

        prepare_process.kill()
