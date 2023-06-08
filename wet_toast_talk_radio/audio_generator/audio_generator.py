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
        nltk.download("punkt")

    def run(self) -> None:
        logger.warning("Not yet implemented")
        pass

    def benchmark(self) -> None:
        """Run audio_generator"""
        # download and load all models
        preload_models()

        script = "Hey there! I'm a dog! Woof woof!"

        logger.info("Tokenizing script into sentences")
        # Need to download punkt tokenizer prior w/ nltk.download()
        sentences = nltk.sent_tokenize(script)

        # save audio to disk
        SPEAKER = "v2/en_speaker_6"
        silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

        logger.info("Starting audio generation")
        logger.debug("Script", script=script)

        start = time.perf_counter()

        pieces = []
        for sentence in sentences:
            logger.info("Generating audio for sentence", sentence=sentence)
            audio_array = generate_audio(sentence, history_prompt=SPEAKER)
            pieces += [audio_array, silence.copy()]

        audio_array = np.concatenate(pieces)

        end = time.perf_counter()
        logger.info("Finished audio generation")

        run_time_in_s = end - start
        duration_in_s = len(audio_array) / SAMPLE_RATE
        speed_ratio = run_time_in_s / duration_in_s
        logger.info(
            "Benchmark results",
            run_time_in_s=round(run_time_in_s, 3),
            duration_in_s=round(duration_in_s, 3),
            speed_ratio=round(speed_ratio, 3),
        )

        uuid_str = str(uuid.uuid4())[:4]
        output_dir = Path.cwd() / "output"
        output_dir.mkdir(exist_ok=True)
        write_wav(
            output_dir / f"bark_generation_{uuid_str}.wav",
            SAMPLE_RATE,
            audio_array,
        )
