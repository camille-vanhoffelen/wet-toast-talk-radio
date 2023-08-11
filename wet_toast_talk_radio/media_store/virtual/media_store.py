import concurrent.futures
import dataclasses
import json
import pathlib
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog

from wet_toast_talk_radio.common.dialogue import Line, read_lines
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import (
    _FALLBACK_KEY,
    MediaStore,
    ShowId,
    ShowMetadata,
    ShowUploadInput,
)
from wet_toast_talk_radio.media_store.virtual.bucket import (
    ShowType,
    VirtualBucket,
    VirtualObject,
)

logger = structlog.get_logger()
_MAX_WORKERS = 3
TXT_ENCODING = "utf-8"


class VirtualMediaStore(MediaStore):
    """
    VirtualMediaStore is a virtual media store that stores media in memory
    VirtualMediaStore is used for testing
    """

    def __init__(self, load_test_data: bool = True):  # noqa: FBT001, FBT002
        self._src_path = pathlib.Path(__file__).parent.with_name("data")
        self._bucket = VirtualBucket()

        today = get_current_iso_utc_date()

        if load_test_data:
            raw_show_i = 0
            default_show_i = 0
            script_show_i = 0
            for file in self._src_path.iterdir():
                if file.is_file():
                    if file.name.endswith(".wav"):
                        with file.open("rb") as f:
                            data = f.read()
                        show_id = ShowId(raw_show_i, today)
                        self.put_raw_show(show_id=show_id, data=data)
                        raw_show_i += 1
                    if file.name.endswith(".mp3"):
                        with file.open("rb") as f:
                            data = f.read()
                        show_id = ShowId(default_show_i, _FALLBACK_KEY)
                        self.put_transcoded_show(show_id=show_id, data=data)
                        default_show_i += 1
                    if file.name.endswith(".jsonl"):
                        lines = read_lines(file)
                        show_id = ShowId(script_show_i, today)
                        self.put_script_show(show_id=show_id, lines=lines)
                        script_show_i += 1

    def put_raw_show(self, show_id: ShowId, data: bytes):
        self._bucket[
            f"{ShowType.RAW.value}/{show_id.store_key()}/show.wav"
        ] = VirtualObject(
            show_id=show_id,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.RAW,
        )

    def put_transcoded_show(self, show_id: ShowId, data: bytes):
        self._bucket[
            f"{ShowType.TRANSCODED.value}/{show_id.store_key()}/show.mp3"
        ] = VirtualObject(
            show_id=show_id,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.TRANSCODED,
        )

    def put_script_show(self, show_id: ShowId, lines: list[Line]):
        text_lines = [line.json() for line in lines]
        content = "\n".join(text_lines)
        data = content.encode(TXT_ENCODING)
        self._bucket[
            f"{ShowType.SCRIPT.value}/{show_id.store_key()}/show.jsonl"
        ] = VirtualObject(
            show_id=show_id,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.SCRIPT,
        )

    def put_script_show_metadata(self, show_id: ShowId, metadata: ShowMetadata):
        content = json.dumps(dataclasses.asdict(metadata))
        data = content.encode(TXT_ENCODING)
        self._bucket[
            f"{ShowType.SCRIPT.value}/{show_id.store_key()}/metadata.json"
        ] = VirtualObject(
            show_id=show_id,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.SCRIPT,
        )

    def upload_transcoded_shows(self, shows: list[ShowUploadInput]):
        def upload_file(path: Path, key: Path, show_id: ShowId):
            with path.open("rb") as f:
                self._bucket[str(key)] = VirtualObject(
                    show_id=show_id,
                    data=f.read(),
                    last_modified=datetime.now(),
                    show_type=ShowType.TRANSCODED,
                )

        def upload_files(show_input: ShowUploadInput):
            filename = "show.mp3"
            path = show_input.show_dir / filename
            key = (
                Path(ShowType.TRANSCODED.value)
                / show_input.show_id.store_key()
                / filename
            )
            upload_file(path=path, key=key, show_id=show_input.show_id)

            filename = "metadata.json"
            path = show_input.show_dir / filename
            key = (
                Path(ShowType.TRANSCODED.value)
                / show_input.show_id.store_key()
                / filename
            )
            upload_file(path=path, key=key, show_id=show_input.show_id)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=_MAX_WORKERS
        ) as executor:
            futures = []
            for show in shows:
                futures.append(executor.submit(upload_files, show))

            concurrent.futures.wait(futures)

    def download_raw_shows(self, show_ids: list[ShowId], dir_output: Path):
        def download_file(show_id: ShowId, dir_output: Path):
            obj = self._bucket.get(
                f"{ShowType.RAW.value}/{show_id.store_key()}/show.wav", None
            )
            if obj:
                new_dir = dir_output / show_id.store_key()
                if not new_dir.exists():
                    new_dir.mkdir(parents=True)
                with (new_dir / "show.wav").open("wb") as f:
                    f.write(obj.data)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=_MAX_WORKERS
        ) as executor:
            futures = []
            for show_id in show_ids:
                futures.append(executor.submit(download_file, show_id, dir_output))
            concurrent.futures.wait(futures)

    def download_script_show(self, show_id: ShowId, dir_output: Path):
        obj = self._bucket.get(
            f"{ShowType.SCRIPT.value}/{show_id.store_key()}/show.jsonl", None
        )
        if not obj:
            raise Exception(f"Show {show_id} not found")

        content = obj.data.decode(TXT_ENCODING)
        new_dir = dir_output / show_id.store_key()
        if not new_dir.exists():
            new_dir.mkdir(parents=True)
        with (new_dir / "show.jsonl").open("w") as f:
            f.write(content)

    def download_script_show_metadata(self, show_id: ShowId, dir_output: Path):
        obj = self._bucket.get(
            f"{ShowType.SCRIPT.value}/{show_id.store_key()}/metadata.json", None
        )
        if not obj:
            raise Exception(f"Show metadata {show_id} not found")

        content = obj.data.decode(TXT_ENCODING)
        new_dir = dir_output / show_id.store_key()
        if not new_dir.exists():
            new_dir.mkdir(parents=True)
        with (new_dir / "metadata.json").open("w") as f:
            f.write(content)

    def get_transcoded_show(self, show_id: str) -> bytes:
        obj = self._bucket.get(
            f"{ShowType.TRANSCODED.value}/{show_id.store_key()}/show.mp3", None
        )
        if obj:
            return obj.data
        return None

    def list_raw_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        return self._list_shows(ShowType.RAW, dates)

    def list_transcoded_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        return self._list_shows(ShowType.TRANSCODED, dates)

    def list_fallback_transcoded_shows(self) -> list[ShowId]:
        ret = []
        for obj in self._bucket.values():
            if obj.show_id.date == _FALLBACK_KEY:
                ret.append(obj.show_id)
        return ret

    def list_script_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        return self._list_shows(ShowType.SCRIPT, dates)

    def _list_shows(
        self, show_type: ShowType, dates: Optional[set[str]] = None
    ) -> list[ShowId]:
        ret = []
        for obj in self._bucket.values():
            if obj.show_type == show_type and obj.show_id.date != _FALLBACK_KEY:
                if dates:
                    if obj.show_id.date in dates:
                        ret.append(obj.show_id)
                else:
                    ret.append(obj.show_id)
        return list(set(ret))
