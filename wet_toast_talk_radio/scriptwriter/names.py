import json
import random
from pathlib import Path

import structlog

logger = structlog.get_logger()


def load_names() -> dict:
    path = Path(__file__).with_name("resources") / "names-ascii.json"
    logger.info("Loading names", path=path)
    with path.open() as f:
        doc = json.load(f)
    return doc


NAMES = load_names()
GENDERS = ["female", "male"]


def random_name(gender: str):
    """Select a random name from the names.json file"""
    if gender not in GENDERS:
        raise ValueError(f"Gender: {gender} must be one of {GENDERS}")
    region = NAMES[random.randrange(len(NAMES))]
    names = region[gender]
    name = names[random.randrange(len(names))]
    return name
