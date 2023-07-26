import time
import uuid
from pathlib import Path

import torchaudio
from tortoise.api import MODELS_DIR, TextToSpeech
from tortoise.utils.audio import load_voices

SAMPLE_RATE = 24000


def benchmark():
    output_dir = Path("results")
    output_dir.mkdir(parents=True, exist_ok=True)

    text_to_speech = TextToSpeech(models_dir=MODELS_DIR, use_deepspeed=False)

    voice_sel = ["random"]
    voice_samples, conditioning_latents = load_voices(voice_sel)

    text = "Hey there! I'm a dog! Woof woof!"

    start = time.perf_counter()

    gen, dbg_state = text_to_speech.tts_with_preset(
        text=text,
        k=1,
        voice_samples=voice_samples,
        conditioning_latents=conditioning_latents,
        preset="ultra_fast",
        use_deterministic_seed=1337,
        return_deterministic_state=True,
        cvvp_amount=0.0,
    )
    audio_array = gen.squeeze(0).cpu()

    end = time.perf_counter()
    run_time_in_s = end - start
    duration_in_s = audio_array.shape[1] / SAMPLE_RATE
    speed_ratio = run_time_in_s / duration_in_s
    print(
        f"Benchmark results: run_time_in_s={round(run_time_in_s, 3)}, duration_in_s={round(duration_in_s, 3)}, speed_ratio={round(speed_ratio, 3)}"
    )

    uuid_str = str(uuid.uuid4())[:4]
    path = output_dir / f"tortoise-benchmark-{uuid_str}.wav"
    torchaudio.save(
        path,
        audio_array,
        SAMPLE_RATE,
    )


if __name__ == "__main__":
    benchmark()
