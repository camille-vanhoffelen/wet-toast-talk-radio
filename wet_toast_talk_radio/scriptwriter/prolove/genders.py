import random
from enum import Enum


class Gender(Enum):
    FEMALE = "female"
    MALE = "male"
    NON_BINARY = "non-binary"

    @classmethod
    def random(cls):
        return random.choice(list(cls))

    def to_noun(self):
        if self == Gender.FEMALE:
            return "a woman"
        if self == Gender.MALE:
            return "a man"
        if self == Gender.NON_BINARY:
            return "non-binary"
