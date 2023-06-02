from pydantic import BaseModel


class AudioGeneratorConfig(BaseModel):
    """audio_generator config file"""

    some_setting: str = "some value"


def validate_config(cfg: AudioGeneratorConfig):
    """Validate config"""
    assert cfg is not None, "AudioGeneratorConfig must not be None"
    assert cfg.some_setting != "", "some_setting must not be empty"
