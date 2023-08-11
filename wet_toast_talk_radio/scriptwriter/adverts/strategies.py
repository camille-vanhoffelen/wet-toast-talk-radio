import random

# Describe product
PART_1_STRATEGIES = [
    "Mention a statistic that provides evidence for the benefits of the product",
    "Make unrealistic claims and promises about the product",
    "Make a detailed and complex technical explanation of how the product works",
    "Use fear-mongering to convince the audience that they need the product",
    "Include a unenthusiastic testimonial of someone who felt the product was kinda OK",
    "Include a excited testimonial of someone who felt the product profoundly changed their life",
    "Enumerate the product's many features in great detail",
    "Enumerate the product's many options in great detail",
    "List some unexpected benefits of the product",
    "Highlight the benefits of the product",
    "Describe the problem that the product solves, then explain how the product solves it",
    "Describe how innovative the product is",
    "Describe the product's unlikely origin story",
    "Make an assumption about the listener which suggests that they need the product",
]

# Sell product
PART_2_STRATEGIES = [
    "Describe one of the company's past controversies, then reassure the audience that the company has changed",
    "Reassure the audience about the excellent safety of the product",
    "Reassure the audience about the unquestionable ethics of the product",
    "Insist that the product is definitely not a scam",
    "Describe the complex pricing structure in great detail, and mention the specific prices",
    "Make a disclaimer about the product's side effects",
    "Offer a special discount for the product, and mention the specific amount",
    "Promote a limited edition version of the product",
    "Make a call to action to buy the product now by visiting the company's website",
    "State the company's slogan",
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
