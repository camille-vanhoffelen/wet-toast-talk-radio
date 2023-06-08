import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path

import structlog
from pydub import AudioSegment

from wet_toast_talk_radio.disc_jockey.config import MediaTranscoderConfig
from wet_toast_talk_radio.media_store import MediaStore

logger = structlog.get_logger()


class MediaTranscoder:
    """MediaTranscoder converts .wav files from a folder to .ogg files and uploads them to the media store"""

    def __init__(
        self, cfg: MediaTranscoderConfig, media_store: MediaStore, tmp_dir=Path("tmp/")
    ) -> None:
        self._cfg = cfg
        self._media_store = media_store
        self._tmp_dir = tmp_dir
        self._raw_shows_dir = self._tmp_dir / "raw"
        self._transcoded_shows_dir = self._tmp_dir / "transcoded"

        for directory in [
            self._raw_shows_dir,
            self._transcoded_shows_dir,
            self._tmp_dir,
        ]:
            if not directory.exists():
                directory.mkdir(parents=True)

    def start(self):
        logger.info(
            "Starting media transcoder...",
            batch_size=self._cfg.batch_size,
            max_transcode_workers=self._cfg.max_transcode_workers,
        )
        new_raw_shows = self._find_new_raw_shows()
        batch = []
        logger.info(
            f"Found {len(new_raw_shows)} new raw shows",
            count=len(new_raw_shows),
            shows=new_raw_shows,
        )
        while new_raw_shows:
            show = new_raw_shows.pop()
            batch.append(show)
            if len(batch) >= self._cfg.batch_size or len(new_raw_shows) == 0:
                logger.info("Processing batch...", batch_len=len(batch), batch=batch)
                self._download_raw_shows(batch)
                self._transcode_downloaded_shows()
                self._upload_tanscoded_shows()
                self._cleanup_tmp_files()
                batch = []
            logger.info(f"{len(new_raw_shows)} shows left to process")

        logger.info("Media transcoder finished!")

    def _find_new_raw_shows(self) -> list[str]:
        """Find new raw shows that have not been transcoded yet"""
        since_one_week = datetime.now() - timedelta(weeks=1)

        transcoded_shows = [
            show.removesuffix(".ogg")
            for show in self._media_store.list_transcoded_shows(since=since_one_week)
        ]
        raw_shows = [
            show.removesuffix(".wav")
            for show in self._media_store.list_raw_shows(since=since_one_week)
        ]
        new_shows = list(set(raw_shows) - set(transcoded_shows))
        return [new_show + ".wav" for new_show in new_shows]

    def _download_raw_shows(self, show_names: list[str]):
        logger.info("Downloading raw shows ...", shows=show_names)
        self._media_store.download_raw_shows(show_names, self._raw_shows_dir)

    def _transcode_downloaded_shows(self):
        logger.info("Transcoding downloaded shows ...")

        def transcode_show(show: Path, out: Path):
            song = AudioSegment.from_mp3(show)
            song.export(out, format="ogg")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._cfg.max_transcode_workers
        ) as executor:
            futures = []
            for raw_show in self._raw_shows_dir.iterdir():
                if raw_show.is_file() and raw_show.suffix == ".wav":
                    out = self._transcoded_shows_dir.joinpath(
                        raw_show.name
                    ).with_suffix(".ogg")
                    futures.append(executor.submit(transcode_show, raw_show, out))

            concurrent.futures.wait(futures)

    def _upload_tanscoded_shows(self):
        logger.info("Uploading transcoded shows ...")
        shows = []
        for transcoded_show in self._transcoded_shows_dir.iterdir():
            if transcoded_show.is_file() and transcoded_show.suffix == ".ogg":
                shows.append(transcoded_show)
        self._media_store.upload_transcoded_shows(shows)

    def _cleanup_tmp_files(self):
        if self._cfg.clean_tmp_dir:
            for directory in [
                self._raw_shows_dir,
                self._transcoded_shows_dir,
            ]:
                for path in directory.iterdir():
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
