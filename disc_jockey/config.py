from pydantic import BaseModel


class DiscJockeyConfig(BaseModel):
    """disc_jockey config file"""

    some_setting: str = "some value"


def validate_config(cfg: DiscJockeyConfig):
    """Validate config"""
    assert cfg is not None, "DiscJockeyConfig must not be None"
    assert cfg.some_setting != "", "some_setting must not be empty"
