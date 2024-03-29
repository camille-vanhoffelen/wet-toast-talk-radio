import random

DEFAULT = (
    "You keep the conversation going about the academic field of {{topic}}, "
    "but you don't really care about what the guest has to say."
)
METAPHOR = (
    "You make a stupid irrelevant metaphor about the academic field of {{topic}}, "
    "and ask the guest if that's what they meant."
)
FAKE_FACT = (
    "You make up a plausible yet farfetched fact about the academic field of {{topic}} and ask the guest about it. "
    "Do not reveal that the fact is made up."
)
CONTROVERSIAL = (
    "You try to make it seem like the guest's answer was highly controversial."
)
PERSONAL_STORY = (
    "You tell an irrelevant mundane personal story that happened to you yesterday, "
    "then you try to relate it to the academic field of {{topic}}."
)
DOOMSTER = "You try to spin the guest's words into something concerning and worrying."
KNOW_BETTER = "You disagree with the guest's answer, and offer an alternative explanation as if you knew better."
PERSONAL_QUESTION = "You ask a rude intrusive personal question that is irrelevant to the academic field of {{topic}}."
ORIGIN_STORY = (
    "You ask the guest how they first got into the academic field of {{topic}}."
)
HIJACK = "You hijack the conversation and make it about yourself."

# Nick always wants to wrap up the show
SUFFIX = " Do not end or wrap up the show."


def random_host_missions(topic: str, k: int) -> list[str]:
    """Randomly sample k missions for the host.
    Sampling without replacement to avoid repetition.
    Oversampling DEFAULT to make it more likely.
    Always start with DEFAULT."""
    missions = [
        DEFAULT,
        METAPHOR,
        FAKE_FACT,
        CONTROVERSIAL,
        PERSONAL_STORY,
        DOOMSTER,
        KNOW_BETTER,
        PERSONAL_QUESTION,
        ORIGIN_STORY,
        HIJACK,
    ]
    missions = [mission.replace("{{topic}}", topic) + SUFFIX for mission in missions]
    counts = [4, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    random_missions = random.sample(population=missions, k=k - 1, counts=counts)
    # always start with default
    return [missions[0], *random_missions]
