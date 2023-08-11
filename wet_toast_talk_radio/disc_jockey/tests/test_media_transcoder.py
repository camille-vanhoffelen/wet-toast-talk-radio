from pathlib import Path
import time
from typing import Generator

import pytest

from wet_toast_talk_radio.disc_jockey.config import MediaTranscoderConfig
from wet_toast_talk_radio.disc_jockey.media_transcoder import MediaTranscoder
from wet_toast_talk_radio.media_store import MediaStore, new_media_store
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.media_store.virtual.bucket import VirtualBucket
from wet_toast_talk_radio.radio_operator.config import RadioOperatorConfig
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator


@pytest.fixture()
def media_store() -> MediaStore:
    media_store = new_media_store(MediaStoreConfig(virtual=True))
    return media_store


@pytest.fixture()
def radio_operator() -> RadioOperator:
    radio_operator = RadioOperator(RadioOperatorConfig())
    return radio_operator


@pytest.fixture(autouse=True)
def _reset():
    VirtualBucket().reset()


@pytest.fixture()
def media_transcoder(
    tmp_path: Generator[Path, None, None], media_store: MediaStore, radio_operator
) -> MediaTranscoder:
    d = tmp_path / "tmp"
    d.mkdir()
    media_transcoder = MediaTranscoder(
        MediaTranscoderConfig(batch_size=3, max_transcode_workers=2),
        media_store,
        radio_operator,
        tmp_dir=d,
    )
    return media_transcoder


class TestMediaTranscoder:
    def test_start(self, media_transcoder: MediaTranscoder, media_store: MediaStore):
        assert len(media_store.list_transcoded_shows()) == 0
        media_transcoder.start()
        assert len(media_store.list_transcoded_shows()) == len(
            media_store.list_raw_shows()
        )

    def test_find_new_raw_shows(
        self, media_transcoder: MediaTranscoder, media_store: MediaStore
    ):
        today = get_current_iso_utc_date()
        show0 = ShowId(0, today)
        media_store.put_transcoded_show(show0, b"raw bytes")
        new_shows = media_transcoder._find_new_raw_shows()
        assert new_shows == [ShowId(1, today)]

    def test_transcode_raw_shows(
        self, media_transcoder: MediaTranscoder, media_store: MediaStore
    ):
        new_shows = media_transcoder._find_new_raw_shows()
        assert len(new_shows) == len(media_store.list_raw_shows())

        media_transcoder._download_raw_shows(new_shows)
        today_raw_shows_dir = (
            media_transcoder._raw_shows_dir / get_current_iso_utc_date()
        )
        assert len(list(today_raw_shows_dir.iterdir())) == len(new_shows)

        media_transcoder._transcode_downloaded_shows()
        today_transcoded_shows_dir = (
            media_transcoder._transcoded_shows_dir / get_current_iso_utc_date()
        )
        assert len(list(today_transcoded_shows_dir.iterdir())) == len(new_shows)
        n_show_files = 2
        assert len(list((today_transcoded_shows_dir / "0").iterdir())) == n_show_files
