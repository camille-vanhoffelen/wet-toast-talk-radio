import requests

from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.radio_operator.config import (
    RadioOperatorConfig,
    validate_config,
)


# https://app.slack.com/block-kit-builder
class RadioOperator:
    """Radio operator allows you to send message to slack"""

    def __init__(self, cfg: RadioOperatorConfig) -> None:
        validate_config(cfg)
        self._enabled = False

        if cfg.web_hook_url is not None:
            self._enabled = True
            self._web_hook_url = cfg.web_hook_url.value()

    def _send(self, block_ui: dict):
        if self._enabled:
            requests.post(self._web_hook_url, json=block_ui)

    def new_playlist(
        self,
        today: str,
        shows: list[ShowId],
        fallback: bool = False,  # noqa: FBT002, FBT001
    ):
        fields = []
        for show in shows:
            fields.append(
                {
                    "type": "plain_text",
                    "text": f"{show.store_key()}",
                }
            )
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
                            "text": f"*{today}*",
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
                        "text": ":rotating_light: *FALLBACK PLAYLIST* :rotating_light:",
                    },
                }
            )

        block_ui["blocks"].append(
            {
                "type": "section",
                "fields": fields,
            },
        )

        self._send(block_ui)
