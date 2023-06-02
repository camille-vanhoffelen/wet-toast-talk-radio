from pydantic import BaseModel

from audio_generator.config import AudioGeneratorConfig
from disc_jockey.config import DiscJockeyConfig


class Config(BaseModel):
    """Root config file"""

    disc_jockey: DiscJockeyConfig | None = None
    audio_generator: AudioGeneratorConfig | None = None
