from pydantic import BaseModel


class ScriptwriterConfig(BaseModel):
    """scriptwriter config file"""

    some_setting: str = "some value"


def validate_config(cfg: ScriptwriterConfig):
    """Validate config"""
    assert cfg is not None, "ScriptwriterConfig must not be None"
    assert cfg.some_setting, "some_setting must not be empty"
