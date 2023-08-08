import random

PRODUCTS = [
    "book",
    "podcast",
    "webseries",
    "blog",
    "essay",
    "nano degree",
    "standup comedy show",
    "merch",
    "hydration drink",
    "video game",
    "dating app",
    "magazine",
    "instagram",
    "tiktok post",
    "love coaching online course",
    "dating online course",
    "online dating seminar",
    "workshop",
    "blind date service",
    "speed dating app",
]


def random_product() -> str:
    """Randomly sample a product for the host of Prolove."""
    return random.choice(PRODUCTS)
