from typing import Optional

from pydantic import BaseModel

from wet_toast_talk_radio.disc_jockey.media_transcoder import MediaTranscoderConfig
from wet_toast_talk_radio.disc_jockey.playlist import PlaylistConfig
from wet_toast_talk_radio.disc_jockey.shout_client import ShoutClientConfig


class DiscJockeyConfig(BaseModel):
    """disc_jockey config file"""

    media_transcoder: Optional[MediaTranscoderConfig] = None
    shout_client: Optional[ShoutClientConfig] = None
    playlist: Optional[PlaylistConfig] = None


def validate_config(cfg: DiscJockeyConfig):
    assert cfg is not None, "DiscJockeyConfig is None"
