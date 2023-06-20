from typing import Optional

from pydantic import BaseSettings

from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig
from wet_toast_talk_radio.disc_jockey.config import DiscJockeyConfig
from wet_toast_talk_radio.emergency_alert_system.config import (
    EmergencyAlertSystemConfig,
)
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.message_queue.config import MessageQueueConfig
from wet_toast_talk_radio.radio_operator.config import RadioOperatorConfig
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig


class RootConfig(BaseSettings):
    """Root config file
    You can use environment variables to override the values in this file following the pattern:
      WT_FIELD_NAME__EMBEDDED_FIELD_NAME=<VALUE>

    You can also use AWS Secrets Manager to store secrets and reference them in this file following the pattern:
      WT_FIELD_NAME__EMBEDDED_FIELD_NAME=sm:/<Secret name>
    When creating a secret in AWS Secrets Manager, make sure the name follows this convention:
      wet_toast_talk_radio/<my_secret>
    """

    disc_jockey: Optional[DiscJockeyConfig] = None
    audio_generator: Optional[AudioGeneratorConfig] = None
    scriptwriter: Optional[ScriptwriterConfig] = None
    media_store: Optional[MediaStoreConfig] = None
    message_queue: Optional[MessageQueueConfig] = None
    radio_operator: Optional[RadioOperatorConfig] = None
    emergency_alert_system: Optional[EmergencyAlertSystemConfig] = None

    class Config:
        env_prefix = "WT_"
        env_nested_delimiter = "__"
