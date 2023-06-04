from pathlib import Path
from typing import Generator

import pytest

from disc_jockey.config import MediaTranscoderConfig
from disc_jockey.media_transcoder import MediaTranscoder
from media_store import MediaStore, new_media_store
from media_store.config import MediaStoreConfig
from media_store.virtual.bucket import VirtualBucket


@pytest.fixture()
def media_store() -> MediaStore:
    media_store = new_media_store(MediaStoreConfig(virtual=True))
    return media_store


@pytest.fixture(autouse=True)
def _reset():
    VirtualBucket().reset()


@pytest.fixture()
def media_transcoder(
    tmp_path: Generator[Path, None, None], media_store: MediaStore
) -> MediaTranscoder:
    d = tmp_path / "tmp"
    d.mkdir()
    media_transcoder = MediaTranscoder(
        MediaTranscoderConfig(batch_size=3, max_transcode_workers=2),
        media_store,
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
        media_store.upload_transcoded_show("show1.ogg", b"raw bytes")
        new_shows = media_transcoder._find_new_raw_shows()
        assert new_shows == ["show2.wav"]

    def test_transcode_raw_shows(
        self, media_transcoder: MediaTranscoder, media_store: MediaStore
    ):
        new_shows = media_transcoder._find_new_raw_shows()
        assert len(new_shows) == len(media_store.list_raw_shows())

        media_transcoder._download_raw_shows(new_shows)
        assert len(list(media_transcoder._raw_shows_dir.iterdir())) == len(new_shows)

        media_transcoder._transcode_downloaded_shows()
        assert len(list(media_transcoder._transcoded_shows_dir.iterdir())) == len(
            new_shows
        )
