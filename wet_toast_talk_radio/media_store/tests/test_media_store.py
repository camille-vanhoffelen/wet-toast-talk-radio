import unittest
from datetime import timedelta
from pathlib import Path
from typing import Generator

import pytest

from wet_toast_talk_radio.common.aws_clients import new_s3_client
from wet_toast_talk_radio.media_store.common.date import (
    get_current_iso_utc_date,
    get_current_utc_date,
)
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import (
    _FALLBACK_KEY,
    ShowId,
    ShowUploadInput,
)
from wet_toast_talk_radio.media_store.new_media_store import new_media_store
from wet_toast_talk_radio.media_store.s3.config import S3Config
from wet_toast_talk_radio.media_store.s3.media_store import S3MediaStore
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore


@pytest.fixture()
def today() -> str:
    return get_current_iso_utc_date()


@pytest.fixture()
def tomorrow() -> str:
    return (get_current_utc_date() + timedelta(days=1)).isoformat()


pytestmark = pytest.mark.parametrize(
    "media_store",
    [
        new_media_store(MediaStoreConfig(virtual=True)),
        pytest.param(
            new_media_store(MediaStoreConfig(virtual=False, s3=S3Config(local=True))),
            marks=pytest.mark.integration(),
        ),
    ],
)

_BUCKET_NAME = "media-store"


@pytest.fixture(autouse=True)
def _setup_bucket(media_store, today) -> list[str]:
    if isinstance(media_store, VirtualMediaStore):
        media_store._bucket.reset()
    elif isinstance(media_store, S3MediaStore):
        s3_client = new_s3_client(local=True)
        response = s3_client.list_objects_v2(Bucket=_BUCKET_NAME)
        if "Contents" in response:
            objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]
            response = s3_client.delete_objects(
                Bucket=_BUCKET_NAME, Delete={"Objects": objects_to_delete}
            )
    else:
        raise Exception("Unknown media store type")

    media_store.put_raw_show(ShowId(0, today), b"raw bytes")
    media_store.put_raw_show(ShowId(1, today), b"raw bytes")
    media_store.put_transcoded_show(ShowId(0, _FALLBACK_KEY), b"raw bytes")
    media_store.put_transcoded_show(ShowId(1, _FALLBACK_KEY), b"raw bytes")
    media_store.put_script_show(ShowId(0, today), "raw bytes")


class TestMediaStore:
    def test_put_raw_show(self, media_store, today: str):
        expected = 2
        assert len(media_store.list_raw_shows()) == expected
        show_id = ShowId(3, today)
        media_store.put_raw_show(show_id, b"raw bytes")
        assert len(media_store.list_raw_shows()) == expected + 1

    def test_put_transcoded_show(self, media_store, today):
        expected = 0
        assert len(media_store.list_transcoded_shows()) == expected
        show_id = ShowId(1, today)
        media_store.put_transcoded_show(show_id, b"raw bytes")
        assert len(media_store.list_transcoded_shows()) == expected + 1

    def test_put_script_show(self, media_store, today):
        expected = 1
        assert len(media_store.list_script_shows()) == expected
        show_id = ShowId(666, today)
        media_store.put_script_show(show_id, "Toast is wet")
        assert len(media_store.list_script_shows()) == expected + 1

    def test_put_transcoded_shows(
        self, media_store, tmp_path: Generator[Path, None, None], today
    ):
        expected = 0
        assert len(media_store.list_transcoded_shows()) == expected

        d = tmp_path / "temp"
        d.mkdir()

        num_shows = 2
        shows = []
        for i in range(num_shows):
            show_path = d.joinpath(f"show{i}.ogg")
            show_path.write_bytes(b"raw bytes")
            shows.append(ShowUploadInput(ShowId(i, today), show_path))

        assert len(list(d.iterdir())) == num_shows

        media_store.upload_transcoded_shows(shows)
        assert len(media_store.list_transcoded_shows()) == num_shows

    def test_download_raw_shows(
        self, media_store, tmp_path: Generator[Path, None, None], today
    ):
        d = tmp_path / "temp"
        d.mkdir()
        wanted_shows = [ShowId(0, today), ShowId(1, today)]
        media_store.download_raw_shows(wanted_shows, d)
        today_dir = d / today
        assert len(list(today_dir.iterdir())) == len(wanted_shows)

    def test_download_script_show(
        self, media_store, tmp_path: Generator[Path, None, None], today
    ):
        d = tmp_path / "temp"
        d.mkdir()
        wanted_show = ShowId(0, today)
        media_store.download_script_show(show_id=wanted_show, dir_output=d)
        today_dir = d / today
        assert len(list(today_dir.iterdir())) == 1

    def test_script_show_encoding(
        self, media_store, tmp_path: Generator[Path, None, None], today
    ):
        d = tmp_path / "temp"
        d.mkdir()
        expected_content = "Toast is wet!"
        show_id = ShowId(666, today)
        media_store.put_script_show(show_id=show_id, content=expected_content)
        media_store.download_script_show(show_id=show_id, dir_output=d)
        actual_content = (d / show_id.store_key() / "show.txt").read_text()
        assert actual_content == expected_content

    def test_list_raw_shows(self, media_store, today, tomorrow):
        case = unittest.TestCase()

        case.assertCountEqual(
            media_store.list_raw_shows(), [ShowId(0, today), ShowId(1, today)]
        )
        media_store.put_raw_show(ShowId(3, today), b"raw bytes")
        case.assertCountEqual(
            media_store.list_raw_shows(),
            [ShowId(0, today), ShowId(1, today), ShowId(3, today)],
        )

        # # upload new raw show 'tomorrow'
        show4 = ShowId(4, tomorrow)
        media_store.put_raw_show(show4, b"raw bytes")
        show5 = ShowId(5, tomorrow)
        media_store.put_raw_show(show5, b"raw bytes")
        case.assertCountEqual(
            media_store.list_raw_shows(dates={tomorrow}), [show4, show5]
        )

    def test_list_transcoded_shows(self, media_store, today, tomorrow):
        case = unittest.TestCase()
        assert len(media_store.list_transcoded_shows()) == 0

        show0 = ShowId(0, today)
        show1 = ShowId(1, today)
        media_store.put_transcoded_show(show0, b"raw bytes1")
        media_store.put_transcoded_show(show1, b"raw bytes2")
        case.assertCountEqual(media_store.list_transcoded_shows(), [show0, show1])

        show4 = ShowId(4, tomorrow)
        media_store.put_transcoded_show(show4, b"raw bytes")
        show5 = ShowId(5, tomorrow)
        media_store.put_transcoded_show(show5, b"raw bytes")
        case.assertCountEqual(
            media_store.list_transcoded_shows(dates={tomorrow}), [show4, show5]
        )

    def test_list_fallback_transcoded_shows(self, media_store):
        case = unittest.TestCase()
        show0 = ShowId(0, _FALLBACK_KEY)
        show1 = ShowId(1, _FALLBACK_KEY)
        expected = [show0, show1]
        fallback_shows = media_store.list_fallback_transcoded_shows()
        assert len(fallback_shows) == len(expected)
        case.assertCountEqual(fallback_shows, expected)

    def test_list_script_shows(self, media_store, today, tomorrow):
        case = unittest.TestCase()

        show0 = ShowId(0, today)
        case.assertCountEqual(media_store.list_script_shows(), [show0])
        show666 = ShowId(666, today)
        media_store.put_script_show(show_id=show666, content="Toast is wet!")
        case.assertCountEqual(media_store.list_script_shows(), [show0, show666])

        show999 = ShowId(999, tomorrow)
        media_store.put_script_show(show999, content="Toast is dry :(")
        case.assertCountEqual(
            media_store.list_script_shows(dates={tomorrow}), [show999]
        )
