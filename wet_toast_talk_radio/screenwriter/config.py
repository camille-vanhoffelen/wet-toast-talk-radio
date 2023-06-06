from pydantic import BaseModel


class ScreenwriterConfig(BaseModel):
    """audio_generator config file"""

    some_setting: str = "some value"


def validate_config(cfg: ScreenwriterConfig):
    """Validate config"""
    assert cfg is not None, "ScreenwriterConfig must not be None"
    assert cfg.some_setting, "some_setting must not be empty"
