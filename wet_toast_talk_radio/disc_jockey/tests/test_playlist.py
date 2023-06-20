from wet_toast_talk_radio.disc_jockey.playlist import Playlist, PlaylistConfig
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import _FALLBACK_KEY, ShowId
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.message_queue.config import StreamMQConfig
from wet_toast_talk_radio.message_queue.new_message_queue import (
    new_stream_message_queue,
)


class TestPlaylist:
    def test_playlist(self):
        today = get_current_iso_utc_date()
        media_store = new_media_store(MediaStoreConfig(virtual=True))
        message_queue = new_stream_message_queue(StreamMQConfig(virtual=True))

        show0 = ShowId(0, today)
        show1 = ShowId(1, today)

        media_store.put_transcoded_show(show0, "foo")
        media_store.put_transcoded_show(show1, "foo")

        playlist = Playlist(PlaylistConfig(), media_store, message_queue)
        playlist.start()

        assert message_queue.get_next_stream_show().show_id == show0
        assert message_queue.get_next_stream_show().show_id == show1

    def test_fallback_playlist(self):
        media_store = new_media_store(MediaStoreConfig(virtual=True))
        message_queue = new_stream_message_queue(StreamMQConfig(virtual=True))

        playlist = Playlist(PlaylistConfig(), media_store, message_queue)
        playlist.start()

        show0 = ShowId(0, _FALLBACK_KEY)
        show1 = ShowId(1, _FALLBACK_KEY)
        assert message_queue.get_next_stream_show().show_id == show0
        assert message_queue.get_next_stream_show().show_id == show1
