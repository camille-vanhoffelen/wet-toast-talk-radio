import random

from wet_toast_talk_radio.common.dialogue import Speaker

HOST = "v2/en_speaker_0"
GUESTS = {
    "male": ["v2/en_speaker_1", "v2/en_speaker_2"],
    "female": ["v2/en_speaker_9", "v2/it_speaker_2"],
}


def get_speaker_prompt(speaker: Speaker) -> str:
    """For given speaker name and gender, return the audio prompt to use for audio generation.
    This decides on the voice and language to use for the voice.
    Host names are given consistent prompts, while guest names are randomly assigned prompts.
    """
    if speaker.name == "Chris":
        return HOST
    else:
        return random.choice(GUESTS[speaker.gender])
