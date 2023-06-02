import logging
import logging.config
import time
import tomllib

import nltk
import numpy as np
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

LOGGING_CONFIG_FILE = "logging-config.toml"

logger = logging.getLogger(__name__)


def setup_logging():
    with open("logging-config.toml", "rb") as f:
        config = tomllib.load(f)
        logging.config.dictConfig(config)

def _print_banner():
    with open("resources/banner.txt", "r") as f:
        banner = f.read()
        logger.info("\n" + banner)

# generate audio from text
def main():
    setup_logging()
    _print_banner()
    # download and load all models
    preload_models()

    with open("resources/noodle-nose.txt", "r") as f:
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
    write_wav("bark_generation.wav", SAMPLE_RATE, audio_array)


if __name__ == "__main__":
    main()
