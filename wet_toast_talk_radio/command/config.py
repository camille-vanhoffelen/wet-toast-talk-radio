from pydantic import BaseModel

from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig
from wet_toast_talk_radio.disc_jockey.config import DiscJockeyConfig
from wet_toast_talk_radio.media_store.config import MediaStoreConfig


class Config(BaseModel):
    """Root config file"""

    disc_jockey: DiscJockeyConfig = DiscJockeyConfig()
    audio_generator: AudioGeneratorConfig | None = None
    media_store: MediaStoreConfig | None = None
