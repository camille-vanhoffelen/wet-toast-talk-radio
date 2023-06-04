import traceback

import structlog

from command import root_cmd
from logger import init_logger

if __name__ == "__main__":
    init_logger()
    logger = structlog.get_logger()

    try:
        root_cmd()
    except Exception:
        logger.error(traceback.format_exc())
