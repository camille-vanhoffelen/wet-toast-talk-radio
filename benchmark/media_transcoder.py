import pathlib
import timeit

import numpy as np
from scipy.io.wavfile import write as write_wav

from wet_toast_talk_radio.disc_jockey.media_transcoder import (
    MediaTranscoder,
    MediaTranscoderConfig,
)
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore
from wet_toast_talk_radio.radio_operator.config import RadioOperatorConfig
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator


def make_white_noise_sample(out: pathlib.Path):
    samplerate = 24000
    duration = 60 * 60  # 1hour
    num_samples = int(samplerate * duration)

    white_noise = np.random.randint(
        np.iinfo(np.int32).min, np.iinfo(np.int32).max, size=num_samples, dtype=np.int32
    )
    write_wav(out, samplerate, white_noise)


if __name__ == "__main__":
    data_path = pathlib.Path(__file__).parent / "data"
    if not data_path.exists():
        data_path.mkdir()
    sample_path = data_path / "white_noise.wav"
    make_white_noise_sample(sample_path)

    today = get_current_iso_utc_date()
    media_store = VirtualMediaStore()
    media_store._bucket.reset()  # noqa: SLF001
    showId = ShowId(0, today)
    media_store.put_raw_show(showId, sample_path.read_bytes())

    radio_operator = RadioOperator(RadioOperatorConfig())

    media_transcoder = MediaTranscoder(
        MediaTranscoderConfig(clean_tmp_dir=False),
        media_store,
        radio_operator,
    )

    res = timeit.Timer(media_transcoder.start).timeit(number=1)
    print(f"\nBenchmark results for 1hour white noise transcoding: \n\tTime={res}")
