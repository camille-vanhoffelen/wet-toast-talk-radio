import random

TRAITS = [
    "boring",
    "hysterical",
    "forgetful",
    "arrogant",
    "offended",
    "proud",
    "deluded",
    "aggressive",
    "defensive",
    "hilarious",
    "passionate",
    "quirky",
    "enigmatic",
    "eccentric",
    "witty",
    "charismatic",
    "pessimistic",
    "awkward",
    "boastful",
    "condescending",
    "narcissistic",
    "tactless",
    "obnoxious",
    "inarticulate",
    "aloof",
    "starstruck",
    "irritable",
    "annoyed",
    "impatient",
    "crazy",
]


def random_trait() -> str:
    """Randomly sample a character trait for the guest of The Expert Zone."""
    return random.choice(TRAITS)
