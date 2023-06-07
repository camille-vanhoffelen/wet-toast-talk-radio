import concurrent.futures
from datetime import datetime, timezone
from pathlib import Path

import boto3
import structlog

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.s3.config import S3Config, validate_config

_RAW_SHOWS_PREFIX = "raw/"
_TRANSCODED_SHOWS_PREFIX = "transcoded/"
logger = structlog.get_logger()


class S3MediaStore(MediaStore):
    """A cloud  media store where objects are stored to s3"""

    def __init__(self, cfg: S3Config):
        validate_config(cfg)
        self.cfg = cfg
        self._bucket_name = cfg.bucket_name
        session = boto3.Session()
        self._s3_client = session.client("s3", endpoint_url=cfg.local_endpoint)

    def upload_raw_show(self, show_name: str, data: bytes):
        if not show_name.endswith(".wav"):
            raise ValueError("show_name must end with .wav")

        key = f"{_RAW_SHOWS_PREFIX}{show_name}"
        self._s3_client.put_object(Bucket=self._bucket_name, Key=key, Body=data)

    def upload_transcoded_show(self, show_name: str, data: bytes):
        if not show_name.endswith(".ogg"):
            raise ValueError("show_name must end with .ogg")

        key = f"{_TRANSCODED_SHOWS_PREFIX}{show_name}"
        self._s3_client.put_object(Bucket=self._bucket_name, Key=key, Body=data)

    def upload_script_show(self, show_name: str, content: str):
        raise NotImplementedError()

    def upload_transcoded_shows(self, show_paths: list[Path]):
        def upload_file(show: Path, key: str):
            try:
                self._s3_client.upload_file(show, self._bucket_name, key)
            except Exception as e:
                logger.error(f"Failed to upload file {show}: {e}")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.cfg.max_workers
        ) as executor:
            futures = []
            for show in show_paths:
                file_name = show.name
                if not file_name:
                    logger.warning(f"Skipping {show} because it has no file name")
                    continue
                if not file_name.endswith(".ogg"):
                    logger.warning(f"Skipping {show} because it does not end with .ogg")
                    continue

                key = f"{_TRANSCODED_SHOWS_PREFIX}{file_name}"
                futures.append(executor.submit(upload_file, show, key))

            concurrent.futures.wait(futures)

    def download_raw_shows(self, show_names: list[str], dir_output: Path):
        def download_file(key: str, file_output: Path):
            try:
                self._s3_client.download_file(self._bucket_name, key, file_output)
            except Exception as e:
                logger.error(f"Failed to download {key} to {file_output}: {e}")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.cfg.max_workers
        ) as executor:
            futures = []
            for show_name in show_names:
                if not show_name.endswith(".wav"):
                    logger.warning(
                        f"Skipping {show_name} because it does not end with .wav"
                    )
                    continue
                key = f"{_RAW_SHOWS_PREFIX}{show_name}"
                file_output = dir_output / show_name
                futures.append(executor.submit(download_file, key, file_output))

            concurrent.futures.wait(futures)

    def download_script_show(self, show_name: str, dir_output: Path):
        raise NotImplementedError()

    def list_raw_shows(self, since: datetime | None = None) -> list[str]:
        return self._list_shows(_RAW_SHOWS_PREFIX, since)

    def list_transcoded_shows(self, since: datetime | None = None) -> list[str]:
        return self._list_shows(_TRANSCODED_SHOWS_PREFIX, since)

    def list_script_shows(self, since: datetime | None = None) -> list[str]:
        raise NotImplementedError()

    def _list_shows(self, prefix: str, since: datetime | None = None) -> list[str]:
        ret = []
        response = self._s3_client.list_objects_v2(
            Bucket=self._bucket_name,
            Prefix=prefix,
        )
        while True:
            if "Contents" in response:
                for obj in response["Contents"]:
                    lastModified = obj["LastModified"]
                    show_name = obj["Key"].removeprefix(prefix)

                    if not since:
                        ret.append(show_name)
                        continue

                    lastModified = lastModified.replace(tzinfo=timezone.utc)
                    since = since.replace(tzinfo=timezone.utc)
                    if lastModified >= since:
                        ret.append(show_name)

            if "NextContinuationToken" in response:
                continuation_token = response["NextContinuationToken"]
                response = self._s3_client.list_objects_v2(
                    Bucket=self._bucket_name,
                    Prefix=prefix,
                    ContinuationToken=continuation_token,
                )
            else:
                break

        return ret
