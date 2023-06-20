import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
    stream_message_queue,  # noqa: F401
    setup_bucket,  # noqa: F401
)
from wet_toast_talk_radio.disc_jockey import DiscJockey
from wet_toast_talk_radio.disc_jockey.config import (
    DiscJockeyConfig,
    MediaTranscoderConfig,
)
from wet_toast_talk_radio.media_store.media_store import ShowId


class TestPlaylist:
    @pytest.mark.integration()
    def test_playlist(
        self, media_store, stream_message_queue, setup_bucket: list[ShowId]  # noqa: F811
    ):
        shows = setup_bucket["raw"]

        cfg = DiscJockeyConfig(
            media_transcoder=MediaTranscoderConfig(clean_tmp_dir=True)
        )

        dj = DiscJockey(cfg, media_store, stream_message_queue)
        dj.transcode_latest_media()
        dj.create_playlist()

        assert stream_message_queue.get_next_stream_show().show_id == shows[0]
        assert stream_message_queue.get_next_stream_show().show_id == shows[1]

    @pytest.mark.integration()
    def test_fallback_playlist(
        self, media_store, stream_message_queue, setup_bucket: list[ShowId]  # noqa: F811
    ):
        shows = setup_bucket["fallback"]

        cfg = DiscJockeyConfig(
            media_transcoder=MediaTranscoderConfig(clean_tmp_dir=True)
        )

        dj = DiscJockey(cfg, media_store, stream_message_queue)
        dj.create_playlist()

        assert stream_message_queue.get_next_stream_show().show_id == shows[0]
        assert stream_message_queue.get_next_stream_show().show_id == shows[1]
