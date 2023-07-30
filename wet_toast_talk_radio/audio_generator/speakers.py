import random
from pathlib import Path

import torch

from wet_toast_talk_radio.common.dialogue import Speaker

HOST = "alex-brodie.pth"
GUESTS = {
    "male": ["ian-lampert.pth", "sean-lenhart.pth"],
    "female": ["karen-cenon.pth", "meghan-christian.pth"],
}

VOICES_DIR = Path(__file__).parent / "resources" / "voices"


def get_conditioning_latents(speaker: Speaker) -> tuple[torch.Tensor, torch.Tensor]:
    """For given speaker name and gender, return the conditioning latent to use for audio generation.
    This determines the voice. Host names are given consistent voices, while guest names are randomly assigned voices.
    """
    voice = HOST if speaker.name == "Chris" else random.choice(GUESTS[speaker.gender])
    return torch.load(VOICES_DIR / voice)
