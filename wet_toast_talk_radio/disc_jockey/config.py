from pydantic import BaseModel


class MediaTranscoderConfig(BaseModel):
    """media_converter config file"""

    max_transcode_workers: int = 3
    batch_size: int = 10


class DiscJockeyConfig(BaseModel):
    """disc_jockey config file"""

    media_converter: MediaTranscoderConfig = MediaTranscoderConfig()


def validate_config(cfg: DiscJockeyConfig):
    assert cfg is not None, "DiscJockeyConfig is None"
