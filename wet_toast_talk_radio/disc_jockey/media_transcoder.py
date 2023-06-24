import concurrent.futures
from datetime import timedelta
from pathlib import Path

import structlog
from pydantic import BaseModel
from pydub import AudioSegment

from wet_toast_talk_radio.common.task_log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_current_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId, ShowUploadInput
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator

logger = structlog.get_logger()


class MediaTranscoderConfig(BaseModel):
    """media_converter config file"""

    clean_tmp_dir: bool = True
    max_transcode_workers: int = 4
    batch_size: int = 4


@task_log_ctx("media_transcoder")
class MediaTranscoder:
    """MediaTranscoder converts .wav files from a folder to .ogg files and uploads them to the media store"""

    def __init__(
        self,
        cfg: MediaTranscoderConfig | None,
        media_store: MediaStore,
        radio_operator: RadioOperator,
        tmp_dir=Path("tmp/"),
    ) -> None:
        if cfg is None:
            cfg = MediaTranscoderConfig()

        self._cfg = cfg
        self._media_store = media_store
        self._radio_operator = radio_operator
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

    def _find_new_raw_shows(self) -> list[ShowId]:
        """Find new raw shows from yesterday, today and tomorrow that have not been transcoded yet"""
        today = get_current_utc_date()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        today_iso = today.isoformat()
        yesterday_iso = yesterday.isoformat()
        tomorrow_iso = tomorrow.isoformat()

        transcoded_shows = self._media_store.list_transcoded_shows(
            dates={today_iso, yesterday_iso, tomorrow_iso}
        )
        raw_shows = self._media_store.list_raw_shows(
            dates={today_iso, yesterday_iso, tomorrow_iso}
        )
        new_shows = []
        for raw_show in raw_shows:
            if raw_show not in transcoded_shows:
                new_shows.append(raw_show)

        return new_shows

    def _download_raw_shows(self, show_ids: list[ShowId]):
        logger.info("Downloading raw shows ...", shows=show_ids)
        self._media_store.download_raw_shows(show_ids, self._raw_shows_dir)

    def _transcode_downloaded_shows(self):
        logger.info("Transcoding downloaded shows ...")

        def transcode_show(show_path: Path, out: Path, show_name: str):
            try:
                song = AudioSegment.from_wav(show_path)
                song.export(out, format="ogg", tags={"title": show_name})
            except Exception as e:
                logger.error("could not transcode show", error=e)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._cfg.max_transcode_workers
        ) as executor:
            futures = []
            for current_dir in self._raw_shows_dir.iterdir():
                # we are in the date folder
                if current_dir.is_dir():
                    date = current_dir.name
                    for show in current_dir.iterdir():
                        new_dir = self._transcoded_shows_dir / date / show.name
                        if not new_dir.exists():
                            new_dir.mkdir(parents=True)
                        out = self._transcoded_shows_dir / date / show.name / "show.ogg"
                        show_path = show / "show.wav"
                        futures.append(
                            executor.submit(
                                transcode_show, show_path, out, f"{date}/{show.name}"
                            )
                        )

            concurrent.futures.wait(futures)

    def _upload_tanscoded_shows(self):
        logger.info("Uploading transcoded shows ...")
        shows = []
        for current_dir in self._transcoded_shows_dir.iterdir():
            # we are in the date folder
            if current_dir.is_dir():
                date = current_dir.name
                for show in current_dir.iterdir():
                    show_id = ShowId(date=date, show_i=show.name)
                    show_upload_input = ShowUploadInput(
                        show_id=show_id, path=show / "show.ogg"
                    )
                    shows.append(show_upload_input)
        self._media_store.upload_transcoded_shows(shows)

    def _cleanup_tmp_files(self):
        if self._cfg.clean_tmp_dir:
            for directory in [
                self._raw_shows_dir,
                self._transcoded_shows_dir,
            ]:
                self._delete_folder(directory)

    def _delete_folder(self, path: Path):
        for sub in path.iterdir():
            if sub.is_dir():
                self._delete_folder(sub)
            else:
                sub.unlink()
        path.rmdir()
