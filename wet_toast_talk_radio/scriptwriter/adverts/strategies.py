import random

# Describe product
PART_1_STRATEGIES = [
    "Make up a fake statistic that supports the benefits of the product",
    "Make unrealistic claims and promises about the product",
    "Make an overly complex technical explanation of the product",
    "Use fear-mongering to convince the audience that they need the product",
    "Include a unenthusiastic testimonial of someone who felt the product was underwhelming",
    "Enumerate the product's many features and variations",
    "List some lackluster benefits of the product",
    "List some unconventional benefits of the product",
    "Highlight the benefits of the product",
    "Describe the problem that the product solves, then explain how the product solves it",
    "Describe how innovative the product is",
    "Make an intrusive statement about why the listener needs the product",
]

# Sell product
PART_2_STRATEGIES = [
    "Mention that the company has put their controversial past behind them",
    "Reassure the audience about the safety of the product",
    "Reassure the audience about the ethics of the product",
    "Insist that the product is definitely not a scam",
    "Describe the confusing pricing structure in great detail",
    "Make a disclaimer about the product's side effects",
    "Create a sense of urgency to buy the product",
    "Make a special offer for the product",
    "Make a call to action to buy the product",
    "Include the company's slogan",
]


def random_strategies(k_part_1: int, k_part_2: int) -> list[str]:
    """Randomly sample advertising strategies.
    k_part_1 is the number of strategies to be sampled
    for the first part of the advert, where the product is introduced.

    k_part_2 is the number of strategies to be sampled
    for the second part of the advert, where the product is sold."""
    part_1_strategies = random.sample(PART_1_STRATEGIES, k=k_part_1)
    part_2_strategies = random.sample(PART_2_STRATEGIES, k=k_part_2)
    return part_1_strategies + part_2_strategies
