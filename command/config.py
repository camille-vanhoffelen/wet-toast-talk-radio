from pydantic import BaseModel

from audio_generator.config import AudioGeneratorConfig
from disc_jockey.config import DiscJockeyConfig
from media_store.config import MediaStoreConfig


class Config(BaseModel):
    """Root config file"""

    disc_jockey: DiscJockeyConfig = DiscJockeyConfig()
    audio_generator: AudioGeneratorConfig | None = None
    media_store: MediaStoreConfig | None = None
