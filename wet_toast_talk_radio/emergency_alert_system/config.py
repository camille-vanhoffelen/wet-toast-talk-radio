from typing import Optional

from pydantic import BaseModel

from wet_toast_talk_radio.common.secret_val import SecretVar


class EmergencyAlertSystemConfig(BaseModel):
    web_hook_url: Optional[SecretVar[str]] = None
