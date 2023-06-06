from pydantic import BaseModel


class MediaTranscoderConfig(BaseModel):
    """media_converter config file"""

    clean_tmp_dir: bool = True
    max_transcode_workers: int = 3
    batch_size: int = 4


class DiscJockeyConfig(BaseModel):
    """disc_jockey config file"""

    media_transcoder: MediaTranscoderConfig = MediaTranscoderConfig()


def validate_config(cfg: DiscJockeyConfig):
    assert cfg is not None, "DiscJockeyConfig is None"
