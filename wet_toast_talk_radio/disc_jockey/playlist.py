import random

import structlog

from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store.common.date import (
    get_current_iso_utc_date,
)
from wet_toast_talk_radio.media_store.media_store import MediaStore, ShowId
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator

logger = structlog.get_logger()

N_FALLBACK_SHOWS = 400


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
        transcoded_shows.sort(key=lambda show_id: show_id.show_i)
        logger.info("Found shows", shows=transcoded_shows)
        if len(transcoded_shows) == 0:
            logger.warning(
                "No shows found for today, using only fallback shows", today=today
            )
            fallback = True
        fallback_shows = self._media_store.list_fallback_transcoded_shows()
        fallback_shows.sort(key=lambda show_id: show_id.show_i)
        fallback_shows = randomize_fallback(fallback_shows)

        # Always use all fallback shows as filler
        all_shows = transcoded_shows + fallback_shows

        self._radio_operator.new_playlist(today, all_shows, fallback)
        return all_shows


def randomize_fallback(fallback_shows: list[ShowId]) -> list[ShowId]:
    """Randomize the order of the fallback shows.
    Picks a random index, and iterates through all elements starting from that index.
    Loops around to the beginning of the list if necessary.
    Maintains show order. Expects sorted list of fallback shows."""
    start = random.randrange(len(fallback_shows))
    end = (start + N_FALLBACK_SHOWS) % len(fallback_shows)
    logger.info("Randomly selected fallback shows", start=start, end=end)
    randomized = fallback_shows[start:] + fallback_shows[:end]
    return randomized
