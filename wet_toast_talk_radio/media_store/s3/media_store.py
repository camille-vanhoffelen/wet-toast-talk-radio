import concurrent.futures
from pathlib import Path
from typing import Optional

import structlog

from wet_toast_talk_radio.common.aws_clients import new_s3_client
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import (
    ShowId,
    ShowUploadInput,
    show_id_from_raw_key,
)
from wet_toast_talk_radio.media_store.s3.config import S3Config, validate_config

_RAW_SHOWS_PREFIX = "raw"
_TRANSCODED_SHOWS_PREFIX = "transcoded"
_SCRIPT_SHOWS_PREFIX = "script"
logger = structlog.get_logger()


class S3MediaStore(MediaStore):
    """A cloud  media store where objects are stored to s3"""

    def __init__(self, cfg: S3Config):
        validate_config(cfg)
        self._cfg = cfg
        self._bucket_name = cfg.bucket_name

    def put_raw_show(self, show_id: ShowId, data: bytes):
        key = f"{_RAW_SHOWS_PREFIX}/{show_id.store_key()}/show.wav"
        new_s3_client(self._cfg.local).put_object(
            Bucket=self._bucket_name, Key=key, Body=data
        )

    def put_transcoded_show(self, show_id: ShowId, data: bytes):
        key = f"{_TRANSCODED_SHOWS_PREFIX}/{show_id.store_key()}/show.ogg"
        new_s3_client(self._cfg.local).put_object(
            Bucket=self._bucket_name, Key=key, Body=data
        )

    def put_script_show(self, show_id: ShowId, content: str):
        key = f"{_SCRIPT_SHOWS_PREFIX}/{show_id.store_key()}/show.txt"
        new_s3_client(self._cfg.local).put_object(
            Bucket=self._bucket_name, Key=key, Body=content
        )

    def upload_transcoded_shows(self, shows: list[ShowUploadInput]):
        def upload_file(show: ShowUploadInput, key: str):
            try:
                new_s3_client(self._cfg.local).upload_file(
                    show.path, self._bucket_name, key
                )
            except Exception as e:
                logger.error(f"Failed to upload file {show}: {e}")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._cfg.max_workers
        ) as executor:
            futures = []
            for show in shows:
                file_name = show.path.name
                if not file_name:
                    logger.warning(f"Skipping {show} because it has no file name")
                    continue
                if not file_name.endswith(".ogg"):
                    logger.warning(f"Skipping {show} because it does not end with .ogg")
                    continue

                key = f"{_TRANSCODED_SHOWS_PREFIX}/{show.show_id.store_key()}/show.ogg"
                futures.append(executor.submit(upload_file, show, key))

            concurrent.futures.wait(futures)

    def download_raw_shows(self, show_ids: list[ShowId], dir_output: Path):
        def download_file(show_id: ShowId, dir_output: Path):
            try:
                key = f"{_RAW_SHOWS_PREFIX}/{show_id.store_key()}/show.wav"
                file_output = dir_output / "show.wav"
                new_s3_client(self._cfg.local).download_file(
                    self._bucket_name, key, file_output
                )
            except Exception as e:
                logger.error(f"Failed to download {key} to {dir_output}: {e}")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._cfg.max_workers
        ) as executor:
            futures = []
            for show_id in show_ids:
                new_dir = dir_output / show_id.store_key()
                if not new_dir.exists():
                    new_dir.mkdir(parents=True)
                futures.append(executor.submit(download_file, show_id, new_dir))

            concurrent.futures.wait(futures)

    def download_script_show(self, show_id: ShowId, dir_output: Path):
        raise NotImplementedError()

    def get_transcoded_show(self, show_id: ShowId) -> bytes:
        key = f"{_TRANSCODED_SHOWS_PREFIX}/{show_id.store_key()}/show.ogg"
        response = new_s3_client(self._cfg.local).get_object(
            Bucket=self._bucket_name, Key=key
        )
        return response["Body"].read()

    def list_raw_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        return self._list_shows(_RAW_SHOWS_PREFIX, dates)

    def list_transcoded_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        return self._list_shows(_TRANSCODED_SHOWS_PREFIX, dates)

    def list_script_shows(self, dates: Optional[set[str]] = None) -> list[ShowId]:
        return self._list_shows(_SCRIPT_SHOWS_PREFIX, dates)

    def _list_shows(
        self, prefix: str, dates: Optional[set[str]] = None
    ) -> list[ShowId]:
        ret = []
        response = new_s3_client(self._cfg.local).list_objects_v2(
            Bucket=self._bucket_name,
            Prefix=prefix,
        )
        while True:
            if "Contents" in response:
                for obj in response["Contents"]:
                    raw_show_id = obj["Key"].removeprefix(prefix + "/")
                    show_id = show_id_from_raw_key(raw_show_id)
                    if dates:
                        if show_id.date in dates:
                            ret.append(show_id)
                    else:
                        ret.append(show_id)

            if "NextContinuationToken" in response:
                continuation_token = response["NextContinuationToken"]
                response = new_s3_client(self._cfg.local).list_objects_v2(
                    Bucket=self._bucket_name,
                    Prefix=prefix,
                    ContinuationToken=continuation_token,
                )
            else:
                break

        return ret
