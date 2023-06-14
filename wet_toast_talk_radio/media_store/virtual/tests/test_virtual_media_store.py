import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest

from wet_toast_talk_radio.media_store.virtual.bucket import ShowType, VirtualBucket
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore


@pytest.fixture(autouse=True)
def _reset():
    virtual_bucket = VirtualBucket()
    virtual_bucket.reset()


class TestVirtualMediaStore:
    def test_upload_raw_show(self):
        virtual_store = VirtualMediaStore()
        expected = 2
        assert len(virtual_store.list_raw_shows()) == expected
        virtual_store.upload_raw_show("show3.wav", b"raw bytes")
        assert len(virtual_store.list_raw_shows()) == expected + 1

    def test_upload_transcoded_show(self):
        virtual_store = VirtualMediaStore()
        expected = 0
        assert len(virtual_store.list_transcoded_shows()) == expected
        virtual_store.upload_transcoded_show("show1.ogg", b"raw bytes")
        assert len(virtual_store.list_transcoded_shows()) == expected + 1

    def test_upload_script_show(self):
        virtual_store = VirtualMediaStore()
        expected = 1
        assert len(virtual_store.list_script_shows()) == expected
        virtual_store.upload_script_show("show666.txt", "Toast is wet")
        assert len(virtual_store.list_script_shows()) == expected + 1

    def test_upload_transcoded_shows(self, tmp_path: Generator[Path, None, None]):
        virtual_store = VirtualMediaStore()
        expected = 0
        assert len(virtual_store.list_transcoded_shows()) == expected

        d = tmp_path / "temp"
        d.mkdir()
        show1 = d.joinpath("show1.ogg")
        show1.write_bytes(b"raw bytes1")
        show2 = d.joinpath("show2.ogg")
        show2.write_bytes(b"raw bytes2")

        expected = 2
        assert len(list(d.iterdir())) == expected

        virtual_store.upload_transcoded_shows([show1, show2])
        assert len(virtual_store.list_transcoded_shows()) == expected

    def test_download_raw_shows(self, tmp_path: Generator[Path, None, None]):
        d = tmp_path / "temp"
        d.mkdir()
        virtual_store = VirtualMediaStore()
        wanted_shows = ["show1.wav", "show2.wav"]
        virtual_store.download_raw_shows(wanted_shows, d)
        assert len(list(d.iterdir())) == len(wanted_shows)

    def test_download_script_show(self, tmp_path: Generator[Path, None, None]):
        d = tmp_path / "temp"
        d.mkdir()
        virtual_store = VirtualMediaStore()
        virtual_store.download_script_show(show_id="show1.txt", dir_output=d)
        assert len(list(d.iterdir())) == 1

    def test_script_show_encoding(self, tmp_path: Generator[Path, None, None]):
        d = tmp_path / "temp"
        d.mkdir()
        virtual_store = VirtualMediaStore()
        expected_content = "Toast is wet!"
        virtual_store.upload_script_show(
            show_id="show666.txt", content=expected_content
        )
        virtual_store.download_script_show(show_id="show666.txt", dir_output=d)
        actual_content = (d / "show666.txt").read_text()
        assert actual_content == expected_content

    def test_list_raw_shows(self):
        case = unittest.TestCase()
        virtual_store = VirtualMediaStore()

        case.assertCountEqual(
            virtual_store.list_raw_shows(), ["show1.wav", "show2.wav"]
        )
        virtual_store.upload_raw_show("show3.wav", b"raw bytes")
        case.assertCountEqual(
            virtual_store.list_raw_shows(), ["show1.wav", "show2.wav", "show3.wav"]
        )

        now = datetime.now()
        # upload new raw show 'tomorrow'
        virtual_store.upload_raw_show("show4.wav", b"raw bytes3")
        virtual_store._bucket[
            f"{ShowType.RAW.value}/show4.wav"
        ].last_modified = now + timedelta(days=1)

        virtual_store.upload_raw_show("show5.wav", b"raw bytes4")
        virtual_store._bucket[
            f"{ShowType.RAW.value}/show5.wav"
        ].last_modified = now + timedelta(days=1)

        case.assertCountEqual(
            virtual_store.list_raw_shows(since=now), ["show4.wav", "show5.wav"]
        )

    def test_list_transcoded_shows(self):
        case = unittest.TestCase()
        virtual_store = VirtualMediaStore()
        assert len(virtual_store.list_transcoded_shows()) == 0

        virtual_store.upload_transcoded_show("show1.ogg", b"raw bytes1")
        virtual_store.upload_transcoded_show("show2.ogg", b"raw bytes2")
        case.assertCountEqual(
            virtual_store.list_transcoded_shows(), ["show1.ogg", "show2.ogg"]
        )

        now = datetime.now()
        # upload  new transcoded show 'tomorrow'
        virtual_store.upload_transcoded_show("show3.ogg", b"raw bytes3")
        virtual_store._bucket[
            f"{ShowType.TRANSCODED.value}/show3.ogg"
        ].last_modified = now + timedelta(days=1)
        virtual_store.upload_transcoded_show("show4.ogg", b"raw bytes4")
        virtual_store._bucket[
            f"{ShowType.TRANSCODED.value}/show4.ogg"
        ].last_modified = now + timedelta(days=1)

        case.assertCountEqual(
            virtual_store.list_transcoded_shows(since=now), ["show3.ogg", "show4.ogg"]
        )

    def test_list_script_shows(self):
        case = unittest.TestCase()
        virtual_store = VirtualMediaStore()

        case.assertCountEqual(virtual_store.list_script_shows(), ["show1.txt"])
        virtual_store.upload_script_show(show_id="show666.txt", content="Toast is wet!")
        case.assertCountEqual(
            virtual_store.list_script_shows(), ["show1.txt", "show666.txt"]
        )

        now = datetime.now()
        # upload new script show 'tomorrow'
        virtual_store.upload_script_show(
            show_id="show999.txt", content="Toast is dry :("
        )
        virtual_store._bucket[
            f"{ShowType.SCRIPT.value}/show999.txt"
        ].last_modified = now + timedelta(days=1)

        case.assertCountEqual(
            virtual_store.list_script_shows(since=now), ["show999.txt"]
        )
