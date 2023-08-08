import random

LESSONS = [
    "self-empowerment",
    "self-love",
    "self-discovery",
    "self-care",
    "self-compassion",
    "self-validation",
    "boundaries",
    "self-acceptance",
    "self-esteem",
    "independence",
]


def random_lesson() -> str:
    """Randomly sample a lesson for the guest of Prolove."""
    return random.choice(LESSONS)
