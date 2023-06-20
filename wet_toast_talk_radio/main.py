import traceback

import structlog

from wet_toast_talk_radio.command import root_cmd
from wet_toast_talk_radio.common.logger import init_logger
from wet_toast_talk_radio.emergency_alert_system.emergency_alert_system import (
    EmergencyAlertSystem,
)

if __name__ == "__main__":
    init_logger()
    logger = structlog.get_logger()
    EmergencyAlertSystem()

    try:
        root_cmd()
    except Exception:
        logger.error(traceback.format_exc())
