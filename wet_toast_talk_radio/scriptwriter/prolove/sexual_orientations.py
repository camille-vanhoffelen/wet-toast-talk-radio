import random

from wet_toast_talk_radio.scriptwriter.prolove.genders import Gender

MALE_SEXUAL_ORIENTATIONS = ["straight", "gay", "queer"]
FEMALE_SEXUAL_ORIENTATIONS = ["straight", "lesbian", "queer"]
NON_BINARY_SEXUAL_ORIENTATIONS = ["queer"]


def random_sexual_orientation(gender: Gender) -> str:
    """Randomly sample a sexual orientation for the guest of Prolove."""
    if gender == Gender.MALE:
        return random.choice(MALE_SEXUAL_ORIENTATIONS)
    if gender == Gender.FEMALE:
        return random.choice(FEMALE_SEXUAL_ORIENTATIONS)
    if gender == Gender.NON_BINARY:
        return random.choice(NON_BINARY_SEXUAL_ORIENTATIONS)
