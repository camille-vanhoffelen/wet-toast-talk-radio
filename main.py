import traceback
import structlog

from command import root_cmd
from logger import init_logger


if __name__ == "__main__":
    init_logger()
    logger = structlog.get_logger()

    try:
        # pylint: disable=no-value-for-parameter
        root_cmd()
    # pylint: disable=broad-except
    except Exception:
        logger.error(traceback.format_exc())
