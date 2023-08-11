import random

TRAITS = [
    "arrogant",
    "pessimistic",
    "boring",
    "chatty",
    "relaxed",
    "shy",
    "proud",
    "obnoxious",
]


def random_trait() -> str:
    """Randomly sample a character trait for the guest of The Expert Zone."""
    return random.choice(TRAITS)
