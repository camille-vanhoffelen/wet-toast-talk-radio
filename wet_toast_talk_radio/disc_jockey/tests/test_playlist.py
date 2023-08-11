import pytest

from wet_toast_talk_radio.disc_jockey.playlist import Playlist
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import _FALLBACK_KEY, ShowId
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.message_queue.config import MessageQueueConfig
from wet_toast_talk_radio.message_queue.new_message_queue import new_message_queue
from wet_toast_talk_radio.radio_operator.config import RadioOperatorConfig
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator


@pytest.fixture()
def radio_operator() -> RadioOperator:
    radio_operator = RadioOperator(RadioOperatorConfig())
    return radio_operator


class TestPlaylist:
    def test_playlist(self, radio_operator):
        today = get_current_iso_utc_date()
        media_store = new_media_store(MediaStoreConfig(virtual=True))
        message_queue = new_message_queue(MessageQueueConfig(virtual=True))

        show0 = ShowId(0, today)
        show1 = ShowId(1, today)

        media_store.put_transcoded_show(show0, "foo")
        media_store.put_transcoded_show(show1, "foo")

        playlist = Playlist(media_store, message_queue, radio_operator)
        playlist.start()

        stream_shows = {message_queue.get_next_stream_show().show_id for _ in range(2)}
        assert stream_shows == {show0, show1}

    def test_fallback_playlist(self, radio_operator):
        media_store = new_media_store(MediaStoreConfig(virtual=True))
        message_queue = new_message_queue(MessageQueueConfig(virtual=True))

        playlist = Playlist(media_store, message_queue, radio_operator)
        playlist.start()

        show0 = ShowId(0, _FALLBACK_KEY)
        show1 = ShowId(1, _FALLBACK_KEY)

        stream_shows = {message_queue.get_next_stream_show().show_id for _ in range(2)}
        assert stream_shows == {show0, show1}
