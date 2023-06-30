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
# Neutral names to prevent biasing character profiles
PLACEHOLDER_NAMES = {
    "in_favor": {"female": "Emily", "male": "Kevin"},
    "against": {"female": "Sarah", "male": "Brian"},
}


def random_name(gender: str):
    """Select a random name from the names.json file"""
    if gender not in GENDERS:
        raise ValueError(f"Gender: {gender} must be one of {GENDERS}")
    region = NAMES[random.randrange(len(NAMES))]
    # TODO consider region randomization
    names = region[gender]
    name = names[random.randrange(len(names))]
    logger.info("Selected random name", name=name)
    return name
