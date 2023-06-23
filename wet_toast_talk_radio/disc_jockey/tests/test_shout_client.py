import multiprocessing
import time
from datetime import timedelta
from multiprocessing.managers import BaseManager

import pytest

from wet_toast_talk_radio.disc_jockey.shout_client import _prepare
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore
from wet_toast_talk_radio.message_queue.virtual.message_queue import VirtualMessageQueue


class VirtualManager(BaseManager):
    pass


VirtualManager.register("MediaStore", VirtualMediaStore)
VirtualManager.register("MessageQueue", VirtualMessageQueue)


@pytest.fixture()
def virtual_manager() -> MediaStore:
    with VirtualManager() as manager:
        yield manager


class TestShoutClient:
    def test_prepare(self, virtual_manager: VirtualManager):
        media_store = virtual_manager.MediaStore()
        message_queue = virtual_manager.MessageQueue()
        today = get_current_iso_utc_date()

        m = multiprocessing.Manager()
        stream_queue = m.Queue(maxsize=1)
        cancel_event = m.Event()

        show0 = ShowId(0, today)
        media_store.put_transcoded_show(show0, "foo")

        prepare_process = multiprocessing.Process(
            target=_prepare,
            args=(
                cancel_event,
                message_queue,
                media_store,
                stream_queue,
                timedelta(microseconds=1),
            ),
        )
        prepare_process.start()
        assert stream_queue.empty()
        message_queue.add_stream_shows([show0])
        time.sleep(1)
        assert stream_queue.full()
        assert stream_queue.get() == ("foo", show0)

        prepare_process.kill()
