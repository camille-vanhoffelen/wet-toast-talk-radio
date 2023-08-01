import json
import random
from pathlib import Path

import structlog

logger = structlog.get_logger()

NAMES_CACHE = None


def load_names() -> dict:
    """Loads names.json file"""
    global NAMES_CACHE  # noqa: PLW0603
    if NAMES_CACHE is not None:
        path = Path(__file__).with_name("resources") / "names-ascii.json"
        logger.info("Loading names", path=path)
        with path.open() as f:
            NAMES_CACHE = json.load(f)
    return NAMES_CACHE


GENDERS = ["female", "male"]


def random_name(gender: str):
    """Loads names.json file and selects a random name"""
    all_names = load_names()
    if gender not in GENDERS:
        raise ValueError(f"Gender: {gender} must be one of {GENDERS}")
    region = all_names[random.randrange(len(all_names))]
    names = region[gender]
    name = names[random.randrange(len(names))]
    return name
