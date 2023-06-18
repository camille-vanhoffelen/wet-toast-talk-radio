import time
import uuid
from pathlib import Path

import nltk
import numpy as np
import structlog
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

from wet_toast_talk_radio.audio_generator.config import (
    AudioGeneratorConfig,
    validate_config,
)
from wet_toast_talk_radio.audio_generator.model_cache import (
    cache_is_present,
    download_model_cache,
)

logger = structlog.get_logger()


class AudioGenerator:
    """Generate audio from text"""

    def __init__(self, cfg: AudioGeneratorConfig, tmp_dir: Path = Path("tmp/")) -> None:
        validate_config(cfg)
        self._cfg = cfg
        self._init_models()
        self._tmp_dir = tmp_dir
        self._raw_shows_dir = self._tmp_dir / "raw"
        if not self._raw_shows_dir.exists():
            self._raw_shows_dir.mkdir(parents=True)

    def run(self) -> None:
        logger.warning("Not yet implemented")
        pass

    def benchmark(self, text: str) -> None:
        """Run audio_generator"""
        # download and load all models
        preload_models()

        logger.info("Tokenizing text into sentences")
        # Need to download punkt tokenizer prior w/ nltk.download()
        sentences = nltk.sent_tokenize(text)

        # save audio to disk
        SPEAKER = "v2/en_speaker_6"
        silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

        logger.info("Starting audio generation")
        logger.debug("Text", text=text)

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
        write_wav(
            self._raw_shows_dir / f"bark_generation_{uuid_str}.wav",
            SAMPLE_RATE,
            audio_array,
        )

    def _init_models(self):
        """Download NLTK model from internet,
        download huggingface hub models from S3 if no local cache"""
        nltk.download("punkt")
        if self._cfg.use_s3_model_cache:
            if not cache_is_present():
                try:
                    download_model_cache()
                except Exception as e:
                    logger.error("Failed to download model cache, continuing", error=e)
            else:
                logger.info("Found local HF hub model cache")
            assert cache_is_present(), "Cache must be complete"
