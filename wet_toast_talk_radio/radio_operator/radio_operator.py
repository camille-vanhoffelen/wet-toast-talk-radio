from typing import Optional

import requests
import structlog

from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.radio_operator.config import (
    RadioOperatorConfig,
)

logger = structlog.get_logger()


# https://app.slack.com/block-kit-builder
class RadioOperator:
    """Radio operator allows you to send message to slack"""

    def __init__(self, cfg: Optional[RadioOperatorConfig]) -> None:
        self._enabled = False
        if cfg is not None and cfg.web_hook_url is not None:
            self._enabled = True
            self._web_hook_url = cfg.web_hook_url.value()
            logger.info("Radio operator enabled")

    def _send(self, block_ui: dict):
        if self._enabled:
            requests.post(self._web_hook_url, json=block_ui)

    def new_playlist(
        self,
        today: str,
        shows: list[ShowId],
        fallback: bool = False,  # noqa: FBT002, FBT001
    ):
        block_ui = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": ":cd:  Playlist  :cd:"},
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "text": f"*{today}*: {len(shows)} shows",
                            "type": "mrkdwn",
                        }
                    ],
                },
                {"type": "divider"},
            ]
        }

        if fallback:
            block_ui["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":rotating_light: *FALLBACK ONLY PLAYLIST* :rotating_light:",
                    },
                }
            )

        self._send(block_ui)
