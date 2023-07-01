import random

from wet_toast_talk_radio.common.dialogue import Speaker

HOST = "v2/en_speaker_0"
GUESTS = {
    "male": ["v2/en_speaker_1", "v2/en_speaker_2"],
    "female": ["v2/en_speaker_9", "v2/it_speaker_2"],
}


def get_speaker_prompt(speaker: Speaker) -> str:
    if speaker.name == "Chris":
        return HOST
    else:
        return random.choice(GUESTS[speaker.gender])
