import random

DETAILS = [
    "Could you tell me more about that, {{name}}? What happened?",
    "I see, {{name}}... can you tell me more details?",
    "Tell me what's going on, {{name}}.",
]

NEW_CALLER = (
    "Oh! It looks like we have a caller on the line. Hello sweetie, you're on the air."
)


def random_host_messages(name: str):
    return [NEW_CALLER, random.choice(DETAILS).replace("{{name}}", name)]
