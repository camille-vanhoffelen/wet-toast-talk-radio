import random

DEFAULT = (
    "You keep the conversation going about {{topic}}, "
    "but you don't really care about what the guest has to say."
)
METAPHOR = "You make a stupid irrelevant metaphor about {{topic}}, and ask the guest if that's what they meant."
CONSPIRACY = "You try to spin the guest's words into a conspiracy theory."
FAKE_FACT = (
    "You make up a plausible yet farfetched fact about {{topic}} and ask the guest about it. "
    "Do not reveal that the fact is made up."
)
CONTROVERSIAL = (
    "You try to make it seem like the guest's answer was highly controversial."
)
PERSONAL_STORY = (
    "You tell an irrelevant mundane personal story that happened to you yesterday, "
    "then you try to relate it to {{topic}}."
)
DOOMSTER = "You try to spin the guest's words into something concerning and worrying."
KNOW_BETTER = "You disagree with the guest's answer, and offer an alternative explanation as if you knew better."
PERSONAL_QUESTION = (
    "You ask a rude intrusive personal question that is irrelevant to {{topic}}."
)


def random_host_missions(topic: str, k: int) -> list[str]:
    """Randomly sample k missions for the host.
    Sampling without replacement to avoid repetition.
    Oversampling DEFAULT to make it more likely."""
    missions = [
        DEFAULT,
        METAPHOR,
        CONSPIRACY,
        FAKE_FACT,
        CONTROVERSIAL,
        PERSONAL_STORY,
        DOOMSTER,
        KNOW_BETTER,
        PERSONAL_QUESTION,
    ]
    missions = [mission.replace("{{topic}}", topic) for mission in missions]
    counts = [4, 1, 1, 1, 1, 1, 1, 1, 1]
    return random.sample(population=missions, k=k, counts=counts)
