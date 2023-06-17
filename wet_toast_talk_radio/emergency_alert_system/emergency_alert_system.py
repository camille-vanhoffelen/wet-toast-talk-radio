import requests
import structlog

from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date


# https://app.slack.com/block-kit-builder
class EmergencyAlertSystem:
    """Emergency Alert System sends a slack message on errors"""

    web_hook_url: str = ""

    def __init__(self) -> None:
        current_processors = structlog.get_config()["processors"]
        processors = current_processors.insert(0, emergency_alert_system_process)
        structlog.configure(processors=processors)


_MAX_SLACK_TEXT_BLOCK_LEN = 3000


# FIX ME
def emergency_alert_system_process(_logger, log_method, event_dict):
    if log_method == "error":
        ctx_vars = structlog.contextvars.get_contextvars()
        task = ctx_vars.get("task", "unkown task")
        event_str = event_dict["event"]
        if len(event_str) > _MAX_SLACK_TEXT_BLOCK_LEN:
            event_str = event_str[len(event_str) - _MAX_SLACK_TEXT_BLOCK_LEN :]
        today = get_current_iso_utc_date()
        block_ui = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":rotating_light:  ERROR  :rotating_light:",
                    },
                },
                {
                    "type": "context",
                    "elements": [{"text": f"*{today}* | {task}", "type": "mrkdwn"}],
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": event_str},
                },
            ],
        }
        send(block_ui)

    return event_dict


def send(block_ui: dict):
    if EmergencyAlertSystem.web_hook_url:
        requests.post(EmergencyAlertSystem.web_hook_url, json=block_ui)
