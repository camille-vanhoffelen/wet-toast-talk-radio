from wet_toast_talk_radio.audio_generator.config import (
    AudioGeneratorConfig,
    validate_config,
)


def test_config():
    cfg = AudioGeneratorConfig()
    validate_config(cfg)
