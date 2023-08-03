import random

TITLES = [
    "Leading Researcher in",
    "Distinguished Researcher in",
    "Research Pioneer in",
    "Research Director in",
    "Distinguished Lecturer in",
    "Professor of",
    "Distinguished Professor of",
    "Endowed Chair Professor of",
    "Professor Emeritus of",
    "Nobel Prize Laureate in",
    "Distinguished Scholar in",
    "Chair of the Royal Society of",
    "Chair of the World Institute of",
]


def random_title() -> str:
    """Randomly sample a prestigious academic title for the guest of The Expert Zone."""
    return random.choice(TITLES)
