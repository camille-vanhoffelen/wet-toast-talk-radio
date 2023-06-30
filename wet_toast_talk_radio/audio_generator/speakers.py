import random

HOST = "v2/en_speaker_0"
GUESTS = {
    "male": ["v2/en_speaker_1", "v2/en_speaker_2"],
    "female": ["v2/en_speaker_9", "v2/it_speaker_2"],
}


def get_speaker_prompt(speaker: str) -> str:
    if speaker == "Chris":
        return HOST
    else:
        # TODO gender select
        return random.choice(GUESTS["male"])
