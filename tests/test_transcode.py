import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
    radio_operator,  # noqa: F401
    setup_bucket,  # noqa: F401
)
from wet_toast_talk_radio.disc_jockey import DiscJockey
from wet_toast_talk_radio.disc_jockey.config import (
    DiscJockeyConfig,
    MediaTranscoderConfig,
)
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.radio_operator.config import RadioOperatorConfig


class TestTranscode:
    @pytest.mark.integration()
    def test_transcode(
        self,
        media_store,  # noqa: F811
        setup_bucket: dict[str, list[ShowId]],  # noqa: F811
        radio_operator,  # noqa: F811
    ):
        raw_shows = setup_bucket["raw"]

        cfg = DiscJockeyConfig(
            media_transcoder=MediaTranscoderConfig(clean_tmp_dir=True),
            radio_operator=RadioOperatorConfig(),
        )

        dj = DiscJockey(cfg, radio_operator, media_store)
        dj.transcode_latest_media()

        assert len(media_store.list_transcoded_shows()) == len(raw_shows)
