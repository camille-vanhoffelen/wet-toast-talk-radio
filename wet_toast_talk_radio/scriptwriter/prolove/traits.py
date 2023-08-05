import random

TRAITS = [
    "shy",
    "hesitant",
    "embarrassed",
    "confused",
    "sad",
    "scared",
    "nervous",
    "happy",
    "starstruck",
    "excited",
    "crazy",
]


def random_trait() -> str:
    """Randomly sample a character trait for the guest of The Expert Zone."""
    return random.choice(TRAITS)
