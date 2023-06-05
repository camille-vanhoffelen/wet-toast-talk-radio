import traceback

import structlog

from wet_toast_talk_radio.command import root_cmd
from wet_toast_talk_radio.logger import init_logger

if __name__ == "__main__":
    init_logger()
    logger = structlog.get_logger()

    try:
        root_cmd()
    except Exception:
        logger.error(traceback.format_exc())
