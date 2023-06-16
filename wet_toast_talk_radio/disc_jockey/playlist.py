from datetime import timedelta
from typing import Optional

import structlog
from pydantic import BaseModel

from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import MediaStore, ShowId
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue

logger = structlog.get_logger()


class PlaylistConfig(BaseModel):
    total_purge_time: int = 60 * 10  # 10 minutes
    purge_wait_time: int = 1  # 1 second


class Playlist:
    def __init__(
        self,
        cfg: Optional[PlaylistConfig],
        media_store: MediaStore,
        message_queue: MessageQueue,
    ) -> None:
        if cfg is None:
            cfg = PlaylistConfig()
        self._cfg = cfg
        self._media_store = media_store
        self._message_queue = message_queue

    def start(self):
        shows = self._find_todays_shows()
        if len(shows) == 0:
            raise Exception("No shows found")

        logger.info("Purging message queue")
        self._message_queue.purge_stream_shows(
            timedelta(seconds=self._cfg.total_purge_time),
            timedelta(seconds=self._cfg.purge_wait_time),
        )

        logger.info("Adding shows to message queue", shows=shows)
        self._message_queue.add_stream_shows(shows)

    def _find_todays_shows(self) -> list[ShowId]:
        today = get_current_iso_utc_date()
        logger.info("Finding today's shows", today=today)
        transcoded_shows = self._media_store.list_transcoded_shows(dates={today})
        if len(transcoded_shows) == 0:
            logger.warning(
                "No shows found for today, using fallback shows", today=today
            )
            transcoded_shows = self._media_store.list_fallback_transcoded_shows()

        logger.info("Found shows", shows=transcoded_shows)
        return transcoded_shows
