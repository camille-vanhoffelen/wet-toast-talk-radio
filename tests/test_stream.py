import multiprocessing
import time
from datetime import timedelta

import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
    message_queue,  # noqa: F401
)
from wet_toast_talk_radio.disc_jockey.shout_client import _prepare
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId


class TestStream:
    @pytest.mark.integration()
    def test_prepare(
        self, _clear_bucket, _clear_sqs, media_store, message_queue  # noqa: PT019, F811
    ):
        today = get_current_iso_utc_date()

        show0 = ShowId(0, today)
        show1 = ShowId(1, today)
        media_store.put_transcoded_show(show0, b"foo0")
        media_store.put_transcoded_show(show1, b"foo1")

        stream_queue = multiprocessing.Queue(maxsize=1)

        prepare_process = multiprocessing.Process(
            target=_prepare,
            args=(message_queue, media_store, stream_queue, timedelta(microseconds=1)),
        )
        prepare_process.start()
        assert stream_queue.empty()

        message_queue.add_stream_shows([show0, show1])
        time.sleep(2)

        assert stream_queue.full()
        assert stream_queue.get() == (b"foo0", show0)
        assert stream_queue.get() == (b"foo1", show1)

        prepare_process.kill()
