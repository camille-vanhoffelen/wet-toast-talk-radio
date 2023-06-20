import pytest

from wet_toast_talk_radio.audio_generator import AudioGenerator
from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig
from wet_toast_talk_radio.media_store.media_store import ShowId


class TestAudioGenerator:
    @pytest.mark.integration()
    def test_transcode(self, media_store, setup_bucket: dict[str, list[ShowId]]):
        scripts = setup_bucket["script"]

        cfg = AudioGeneratorConfig(use_s3_model_cache=False)

        audio_generator = AudioGenerator(cfg=cfg, media_store=media_store)
        audio_generator.run()

        assert len(media_store.list_raw_shows()) == len(scripts)
