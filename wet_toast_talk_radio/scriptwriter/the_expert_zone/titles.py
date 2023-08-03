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
    "Endowed Chair Professor of",
    "Nobel Prize Laureate in",
    "Dean of the Faculty of",
    "Distinguished Scholar in",
    "Fellow of the Academy of",
    "Chair of the Royal Society of",
    "Chair of the World Institute of",
    "President of the National Center of",
    "President of the National Academy of",
]


def random_title() -> str:
    """Randomly sample a prestigious academic title for the guest of The Expert Zone."""
    return random.choice(TITLES)
