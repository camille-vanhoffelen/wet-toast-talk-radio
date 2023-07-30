import random
from pathlib import Path

import structlog
import torch

from wet_toast_talk_radio.common.dialogue import Speaker

logger = structlog.get_logger()

HOST = "alex-brodie.pth"
GUESTS = {
    "male": ["ian-lampert.pth", "sean-lenhart.pth"],
    "female": ["karen-cenon.pth", "meghan-christian.pth"],
}

VOICES_DIR = Path(__file__).parent / "resources" / "voices"


def init_voice_cache():
    """Load all host voices into memory."""
    logger.info("Initiliazing voice cache")
    return {"Chris": load_conditioning_latent(VOICES_DIR / HOST)}


def get_conditioning_latents(
    speaker: Speaker, voice_cache: dict[str, tuple[torch.Tensor, torch.Tensor]]
) -> tuple[torch.Tensor, torch.Tensor]:
    """For given speaker name and gender, return the conditioning latent to use for audio generation.
    This determines the voice. Host names are given consistent voices, while guest names are randomly assigned voices.
    A voice cache is used to keep consistent guest voices, and only load them once.
    """
    if voice_cache is None:
        raise ValueError("Voice cache must be initialized before use")
    if speaker.name in voice_cache:
        return voice_cache[speaker.name]
    else:
        voice = random.choice(GUESTS[speaker.gender])
        conditioning_latents = load_conditioning_latent(VOICES_DIR / voice)
        voice_cache[speaker.name] = conditioning_latents
        return conditioning_latents


def load_conditioning_latent(path: Path) -> tuple[torch.Tensor, torch.Tensor]:
    return torch.load(path, map_location=torch.device("cpu"))
