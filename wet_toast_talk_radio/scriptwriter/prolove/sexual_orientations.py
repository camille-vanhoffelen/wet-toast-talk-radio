import random

from wet_toast_talk_radio.scriptwriter.prolove.genders import Gender

SEXUAL_ORIENTATIONS = ["heterosexual", "homosexual", "pansexual"]
RANDOM_WEIGHTS = {
    Gender.MALE: [70, 20, 10],
    Gender.FEMALE: [70, 10, 20],
    Gender.NON_BINARY: [5, 5, 90],
}


def random_sexual_orientation(gender: Gender) -> str:
    """Randomly sample a sexual orientation for the guest of Prolove."""
    weights = RANDOM_WEIGHTS[gender]
    return random.choices(SEXUAL_ORIENTATIONS, weights=weights, k=1)[0]
