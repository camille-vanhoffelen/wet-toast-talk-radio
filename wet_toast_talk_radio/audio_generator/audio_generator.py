import time
import uuid
from io import BytesIO
from pathlib import Path
from typing import Callable

import numpy as np
import structlog
from scipy.io.wavfile import write as write_wav
from tortoise.api import MODELS_DIR, TextToSpeech
from tortoise.utils.text import split_and_recombine_text

from wet_toast_talk_radio.audio_generator.config import (
    AudioGeneratorConfig,
    validate_config,
)
from wet_toast_talk_radio.audio_generator.speakers import get_conditioning_latents
from wet_toast_talk_radio.common.dialogue import Line, read_lines
from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.common.path import delete_folder
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue

logger = structlog.get_logger()

SAMPLE_RATE = 24000
SILENCE = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence


@task_log_ctx("audio_generator")
class AudioGenerator:
    """Generate audio from text"""

    def __init__(
        self,
        cfg: AudioGeneratorConfig,
        media_store: MediaStore | None = None,
        message_queue: MessageQueue | None = None,
        tmp_dir: Path = Path("tmp/"),
    ) -> None:
        validate_config(cfg)
        logger.info("Initializing audio_generator")
        self.seed = 1337
        self._cfg = cfg
        self._media_store = media_store
        self._message_queue = message_queue

        self._tmp_dir = tmp_dir
        self._script_shows_dir = self._tmp_dir / "script"
        self._script_shows_dir.mkdir(parents=True, exist_ok=True)

        self.tts = TextToSpeech(
            models_dir=MODELS_DIR,
            use_deepspeed=False,
            kv_cache=True,
            half=True,
            enable_redaction=False,
        )

    def run(
        self,
    ) -> None:
        """Reads script shows from message_queue, generates audio, and uploads to media_store"""
        logger.info("Starting audio generator...")
        assert (
            self._media_store is not None
        ), "MediaStore must be provided to run AudioGenerator"
        while script_show_message := self._message_queue.poll_script_show():
            show_id = script_show_message.show_id
            logger.info("Generating audio for script show", show_id=show_id)
            self._media_store.download_script_show(
                show_id=show_id, dir_output=self._script_shows_dir
            )
            script = read_lines(
                self._script_shows_dir / show_id.store_key() / "show.jsonl"
            )

            def heartbeat():
                self._message_queue.change_message_visibility_timeout(
                    receipt_handle=script_show_message.receipt_handle,
                    timeout_in_s=self._cfg.heartbeat_interval_in_s,
                )

            data = self._script_to_audio(lines=script, sentence_callbacks=[heartbeat])
            self._media_store.put_raw_show(show_id=show_id, data=data)
            self._message_queue.delete_script_show(script_show_message.receipt_handle)
            logger.info("Show deleted from message_queue", show_id=show_id)
            if self._cfg.clean_tmp_dir:
                delete_folder(self._script_shows_dir)
        logger.info("Script shows queue empty, Audio Generator exiting")

    def benchmark(self, lines: list[Line]) -> None:
        """Benchmark audio_generator speed"""
        logger.info("Starting audio generator benchmark...")
        data = self._script_to_audio(lines)
        uuid_str = str(uuid.uuid4())[:4]
        path = self._tmp_dir / f"audio-generator-benchmark-{uuid_str}.wav"
        logger.info("Writing audio to file", path=path)
        with path.open("wb") as f:
            f.write(data)
        logger.info("Audio generator benchmark finished!")

    def _script_to_audio(
        self, lines: list[Line], sentence_callbacks: list[Callable] | None = None
    ) -> bytes:
        logger.info("Starting audio generation")
        start = time.perf_counter()

        pieces = []
        for line in lines:
            pieces.append(
                self._line_to_audio(line=line, sentence_callbacks=sentence_callbacks)
            )

        logger.debug("Concatenating line audio pieces")
        audio_array = np.concatenate(pieces)

        # np.int32 is needed in order for the wav file to end up begin 32bit width
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html#scipy-io-wavfile-write
        audio_array = self._to_pcm(audio_array)

        buffer = BytesIO()
        write_wav(
            filename=buffer,
            rate=SAMPLE_RATE,
            data=audio_array,
        )

        end = time.perf_counter()
        run_time_in_s = end - start
        duration_in_s = len(audio_array) / SAMPLE_RATE
        speed_ratio = run_time_in_s / duration_in_s
        logger.info(
            "Benchmark results",
            run_time_in_s=round(run_time_in_s, 3),
            duration_in_s=round(duration_in_s, 3),
            speed_ratio=round(speed_ratio, 3),
        )

        return buffer.getvalue()

    def _line_to_audio(
        self, line: Line, sentence_callbacks: list[Callable] | None
    ) -> np.ndarray:
        chunks = split_and_recombine_text(line.content)
        logger.debug("Split line into chunks", n_chunks=len(chunks))

        conditioning_latents = get_conditioning_latents(speaker=line.speaker)

        pieces = []
        for i, chunk in enumerate(chunks):
            logger.info(
                "Generating audio for chunk",
                chunk=chunk,
                progress=f"{i + 1}/{len(chunks)}",
            )
            gen = self.tts.tts_with_preset(
                text=chunk,
                k=1,
                conditioning_latents=conditioning_latents,
                preset="ultra_fast",
                use_deterministic_seed=self.seed,
                return_deterministic_state=False,
                cvvp_amount=0.0,
                verbose=False,
            )
            audio_array = gen.squeeze().cpu()
            pieces += [audio_array, SILENCE.copy()]
            if sentence_callbacks:
                [c() for c in sentence_callbacks]

        logger.debug("Concatenating chunk audio pieces")
        audio_array = np.concatenate(pieces)
        return audio_array

    def _to_pcm(self, sig, dtype: str = "int32") -> np.ndarray:
        """Convert floating point signal with a range from -1 to 1 to PCM.
        Any signal values outside the interval [-1.0, 1.0) are clipped.
        No dithering is used.
        Note that there are different possibilities for scaling floating
        point numbers to PCM numbers, this function implements just one of
        them.  For an overview of alternatives see
        http://blog.bjornroche.com/2009/12/int-float-int-its-jungle-out-there.html
        """
        logger.debug("Converting to audio to PCM", dtype=dtype)
        dtype = np.dtype(dtype)
        if sig.dtype.kind != "f":
            raise TypeError("'sig' must be a float array")
        if dtype.kind not in "iu":
            raise TypeError("'dtype' must be an integer type")

        i = np.iinfo(dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)
