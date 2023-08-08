import random
from enum import Enum

# 0.3% of the US population is non-binary
# boosted to 4% to make guests more varied
WEIGHTS = [48, 48, 4]


class Gender(Enum):
    FEMALE = "female"
    MALE = "male"
    NON_BINARY = "non-binary"

    @classmethod
    def random(cls):
        return random.choices(list(cls), weights=WEIGHTS, k=1)[0]

    def to_noun(self):
        if self == Gender.FEMALE:
            return "a woman"
        if self == Gender.MALE:
            return "a man"
        if self == Gender.NON_BINARY:
            return "non-binary"
