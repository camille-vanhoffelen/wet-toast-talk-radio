import time
import uuid
from pathlib import Path

import nltk
import numpy as np
import structlog
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig

logger = structlog.get_logger()


class AudioGenerator:
    """Generate audio from text"""

    def __init__(self, cfg: AudioGeneratorConfig):
        self._cfg = cfg

    def run(self) -> None:
        logger.warning("Not yet implemented")
        pass

    def benchmark(self) -> None:
        """Run audio_generator"""
        # download and load all models
        preload_models()

        with Path("audio_generator/resources/noodle-nose.txt").open(
            "r", encoding="utf-8"
        ) as f:
            script = f.read()

        # TODO remove
        script = "Hey there! I'm a dog! Woof woof!"

        logger.info("Tokenizing script into sentences")
        # Need to download punkt tokenizer prior w/ nltk.download()
        sentences = nltk.sent_tokenize(script)

        # save audio to disk
        SPEAKER = "v2/en_speaker_6"
        silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

        logger.info("Starting audio generation")
        start = time.perf_counter()

        pieces = []
        for sentence in sentences:
            logger.info(f"Generating audio for: {sentence}")
            audio_array = generate_audio(sentence, history_prompt=SPEAKER)
            pieces += [audio_array, silence.copy()]

        end = time.perf_counter()
        logger.info(f"Audio generation took {end - start:0.3f} seconds")

        audio_array = np.concatenate(pieces)

        uuid_str = str(uuid.uuid4())[:4]
        write_wav(f"bark_generation_{uuid_str}.wav", SAMPLE_RATE, audio_array)
