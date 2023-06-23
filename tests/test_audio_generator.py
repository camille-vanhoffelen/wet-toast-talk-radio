import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
    radio_operator,  # noqa: F401
    setup_bucket,  # noqa: F401
)
from wet_toast_talk_radio.audio_generator import AudioGenerator
from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig
from wet_toast_talk_radio.media_store.media_store import ShowId


class TestAudioGenerator:
    @pytest.mark.integration()
    def test_transcode(
        self,
        media_store,  # noqa: F811
        setup_bucket: dict[str, list[ShowId]],  # noqa: F811
    ):
        scripts = setup_bucket["script"]

        cfg = AudioGeneratorConfig(use_s3_model_cache=False, use_small_models=True)
        audio_generator = AudioGenerator(cfg=cfg, media_store=media_store)
        audio_generator.run()

        for s in scripts:
            assert s in media_store.list_raw_shows()
