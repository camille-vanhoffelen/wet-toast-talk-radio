import json
import random
from pathlib import Path

import structlog
import torch

from wet_toast_talk_radio.common.dialogue import Speaker

logger = structlog.get_logger()

VOICES_DIR = Path(__file__).parent / "resources" / "voices"
VOICES_METADATA_PATH = Path(__file__).parent / "resources" / "voices-metadata.json"


def read_voices_metadata() -> dict:
    with VOICES_METADATA_PATH.open() as f:
        return json.load(f)


VOICES_METADATA = read_voices_metadata()
HOSTS = VOICES_METADATA["hosts"]["female"] + VOICES_METADATA["hosts"]["male"]
VOICE_EXT = ".pth"


def init_voices(speakers: set[Speaker]) -> dict[str, tuple[torch.Tensor, torch.Tensor]]:
    """Initialize voice conditioning latents for each speaker in the dialogue.
    Assumes that each speaker has a unique name."""
    voices = {}

    hosts = [speaker for speaker in speakers if speaker.host]
    for speaker in hosts:
        if speaker.name.lower() not in HOSTS:
            raise ValueError("Host name not found in host voices metadata")
        voices[speaker.name] = load_conditioning_latent(
            VOICES_DIR / (speaker.name.lower() + VOICE_EXT)
        )

    guests = [speaker for speaker in speakers if not speaker.host]

    female_guests = [guest for guest in guests if guest.gender == "female"]
    # Picking without replacement ensures that each guest gets a unique voice
    female_voice_ids = random.sample(
        VOICES_METADATA["guests"]["female"], len(female_guests)
    )
    for speaker, voice_id in zip(female_guests, female_voice_ids, strict=True):
        voices[speaker.name] = load_conditioning_latent(
            VOICES_DIR / (voice_id + VOICE_EXT)
        )

    male_guests = [guest for guest in guests if guest.gender == "male"]
    male_voice_ids = random.sample(VOICES_METADATA["guests"]["male"], len(male_guests))
    for speaker, voice_id in zip(male_guests, male_voice_ids, strict=True):
        voices[speaker.name] = load_conditioning_latent(
            VOICES_DIR / (voice_id + VOICE_EXT)
        )
    # TODO also do pick without replacement for names ACROSS genders

    return voices


def load_conditioning_latent(path: Path) -> tuple[torch.Tensor, torch.Tensor]:
    return torch.load(path, map_location=torch.device("cpu"))
