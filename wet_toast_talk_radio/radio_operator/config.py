from typing import Optional

from pydantic import BaseModel

from wet_toast_talk_radio.common.secret_val import SecretVar


class RadioOperatorConfig(BaseModel):
    """scriptwriter config file"""

    web_hook_url: Optional[SecretVar[str]] = None


def validate_config(cfg: RadioOperatorConfig):
    """Validate config"""
    assert cfg is not None, "RadioOperatorConfig must not be None"
