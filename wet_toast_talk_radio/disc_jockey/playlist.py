import structlog

from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store.common.date import (
    get_current_iso_utc_date,
)
from wet_toast_talk_radio.media_store.media_store import MediaStore, ShowId
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator

logger = structlog.get_logger()


@task_log_ctx("playlist")
class Playlist:
    def __init__(
        self,
        media_store: MediaStore,
        message_queue: MessageQueue,
        radio_operator: RadioOperator,
    ) -> None:
        self._media_store = media_store
        self._message_queue = message_queue
        self._radio_operator = radio_operator

    def start(self):
        shows = self._find_todays_shows()
        if len(shows) == 0:
            raise Exception("No shows found")

        self._message_queue.purge_stream_shows()

        logger.info("Adding shows to message queue", shows=shows)
        self._message_queue.add_stream_shows(shows)

    def _find_todays_shows(self) -> list[ShowId]:
        today = get_current_iso_utc_date()
        fallback = False
        logger.info("Finding today's shows", today=today)
        transcoded_shows = self._media_store.list_transcoded_shows(dates={today})
        if len(transcoded_shows) == 0:
            logger.warning(
                "No shows found for today, using fallback shows", today=today
            )
            transcoded_shows = self._media_store.list_fallback_transcoded_shows()
            fallback = True

        logger.info("Found shows", shows=transcoded_shows)
        self._radio_operator.new_playlist(today, transcoded_shows, fallback)
        return transcoded_shows
