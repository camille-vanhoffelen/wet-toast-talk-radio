import concurrent.futures
import pathlib
from datetime import datetime
from pathlib import Path

import structlog

from wet_toast_talk_radio.media_store.media_store import MediaStore
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

    def __init__(self):
        self._src_path = pathlib.Path(__file__).with_name("data")
        self._bucket = VirtualBucket()

        for file in self._src_path.iterdir():
            if file.is_file():
                if file.name.endswith(".wav"):
                    with file.open("rb") as f:
                        data = f.read()
                    self.upload_raw_show(show_name=file.name, data=data)
                if file.name.endswith(".txt"):
                    with file.open("r") as f:
                        content = f.read()
                    self.upload_script_show(show_name=file.name, content=content)

    def upload_raw_show(self, show_name: str, data: bytes):
        if not show_name.endswith(".wav"):
            raise ValueError("show_name must end with .wav")
        self._bucket[f"{ShowType.RAW.value}/{show_name}"] = VirtualObject(
            show_name=show_name,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.RAW,
        )

    def upload_transcoded_show(self, show_name: str, data: bytes):
        if not show_name.endswith(".ogg"):
            raise ValueError("show_name must end with .wav")
        self._bucket[f"{ShowType.TRANSCODED.value}/{show_name}"] = VirtualObject(
            show_name=show_name,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.TRANSCODED,
        )

    def upload_script_show(self, show_name: str, content: str):
        if not show_name.endswith(".txt"):
            raise ValueError("show_name must end with .txt")
        data = content.encode(TXT_ENCODING)
        self._bucket[f"{ShowType.SCRIPT.value}/{show_name}"] = VirtualObject(
            show_name=show_name,
            data=data,
            last_modified=datetime.now(),
            show_type=ShowType.SCRIPT,
        )

    def upload_transcoded_shows(self, show_paths: list[Path]):
        def upload_file(show: Path, key: str):
            with show.open("rb") as f:
                self._bucket[key] = VirtualObject(
                    show_name=show.name,
                    data=f.read(),
                    last_modified=datetime.now(),
                    show_type=ShowType.TRANSCODED,
                )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=_MAX_WORKERS
        ) as executor:
            futures = []
            for show in show_paths:
                file_name = show.name
                if not file_name:
                    logger.warning(f"Skipping {show} because it has no file name")
                    continue
                key = f"{ShowType.TRANSCODED.value}/{file_name}"
                futures.append(executor.submit(upload_file, show, key))

            concurrent.futures.wait(futures)

    def download_raw_shows(self, show_names: list[str], dir_output: Path):
        def download_file(show_name: str, dir_output: Path):
            obj = self._bucket.get(f"{ShowType.RAW.value}/{show_name}", None)
            if obj:
                with (dir_output / show_name).open("wb") as f:
                    f.write(obj.data)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=_MAX_WORKERS
        ) as executor:
            futures = []
            for show_name in show_names:
                futures.append(executor.submit(download_file, show_name, dir_output))
            concurrent.futures.wait(futures)

    def download_script_show(self, show_name: str, dir_output: Path):
        obj = self._bucket.get(f"{ShowType.SCRIPT.value}/{show_name}", None)
        content = obj.data.decode(TXT_ENCODING)
        if obj:
            with (dir_output / show_name).open("w") as f:
                f.write(content)

    def list_raw_shows(self, since: datetime | None = None) -> list[str]:
        return self._list_shows(ShowType.RAW, since)

    def list_transcoded_shows(self, since: datetime | None = None) -> list[str]:
        return self._list_shows(ShowType.TRANSCODED, since)

    def list_script_shows(self, since: datetime | None = None) -> list[str]:
        return self._list_shows(ShowType.SCRIPT, since)

    def _list_shows(
        self, show_type: ShowType, since: datetime | None = None
    ) -> list[str]:
        ret = []
        for obj in self._bucket.values():
            if obj.show_type == show_type:
                if not since:
                    ret.append(obj.show_name)
                    continue

                if obj.last_modified > since:
                    ret.append(obj.show_name)
        return ret
