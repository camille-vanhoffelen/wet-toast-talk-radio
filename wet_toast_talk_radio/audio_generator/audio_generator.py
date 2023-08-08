import time
import uuid
from io import BytesIO
from pathlib import Path
from typing import Callable

import librosa
import numpy as np
import structlog
import torch
from librosa import resample
from scipy.io.wavfile import write as write_wav
from tortoise.api import MODELS_DIR, TextToSpeech
from tortoise.utils.text import split_and_recombine_text
from voicefixer import VoiceFixer

from wet_toast_talk_radio.audio_generator.cache import (
    MODERN_MINDFULNESS_BACKGROUND_PATH,
    cache_is_present,
    download_model_cache,
)
from wet_toast_talk_radio.audio_generator.config import (
    AudioGeneratorConfig,
    validate_config,
)
from wet_toast_talk_radio.audio_generator.speakers import init_voices
from wet_toast_talk_radio.common.dialogue import Line, read_lines
from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.common.path import delete_folder
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue, ShowType

logger = structlog.get_logger()

SAMPLE_RATE = 24000
SILENCE = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence
OUTPUT_SAMPLE_RATE = 44100


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

        self._init_models()

        self.tts = TextToSpeech(
            models_dir=MODELS_DIR,
            use_deepspeed=False,
            kv_cache=True,
            half=True,
            enable_redaction=False,
        )
        self.vf = VoiceFixer()

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
            show_type = script_show_message.show_type
            logger.info(
                "Generating audio for script show", show_id=show_id, show_type=show_type
            )
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

            background_music = bool(show_type == ShowType.MODERN_MINDFULNESS)
            data = self._script_to_audio(
                lines=script,
                background_music=background_music,
                sentence_callbacks=[heartbeat],
            )
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
        self,
        lines: list[Line],
        background_music: bool = False,  # noqa: FBT001, FBT002
        sentence_callbacks: list[Callable] | None = None,
    ) -> bytes:
        logger.info("Starting audio generation")
        start = time.perf_counter()

        # Reset voices for each new script
        speakers = {line.speaker for line in lines}
        voices = init_voices(speakers)

        pieces = []
        for line in lines:
            pieces.append(
                self._line_to_audio(
                    line=line,
                    sentence_callbacks=sentence_callbacks,
                    voices=voices,
                )
            )

        logger.debug("Concatenating line audio pieces")
        audio_array = np.concatenate(pieces)

        audio_array, sample_rate = self._postprocess(
            audio_array, background_music=background_music
        )

        buffer = BytesIO()
        write_wav(
            filename=buffer,
            rate=sample_rate,
            data=audio_array,
        )

        end = time.perf_counter()
        run_time_in_s = end - start
        duration_in_s = len(audio_array) / sample_rate
        speed_ratio = run_time_in_s / duration_in_s
        logger.info(
            "Benchmark results",
            run_time_in_s=round(run_time_in_s, 3),
            duration_in_s=round(duration_in_s, 3),
            speed_ratio=round(speed_ratio, 3),
        )

        return buffer.getvalue()

    def _line_to_audio(
        self,
        line: Line,
        sentence_callbacks: list[Callable] | None,
        voices: dict[str, tuple[torch.Tensor, torch.Tensor]],
    ) -> np.ndarray:
        chunks = split_and_recombine_text(
            line.content, desired_length=150, max_length=250
        )
        chunks = [c.replace("-", " ") for c in chunks]
        logger.debug("Split line into chunks", n_chunks=len(chunks))
        # Replace hyphens with spaces to avoid weird pauses

        conditioning_latents = voices[line.speaker.name]

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
                speaking_rate=line.speaker.speaking_rate,
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

    @staticmethod
    def _add_background_music(audio_array: np.ndarray) -> np.ndarray:
        """Add background music to audio"""
        logger.info("Adding background music")
        background = librosa.load(MODERN_MINDFULNESS_BACKGROUND_PATH)
        # cropping to match audio length
        background = background[: len(audio_array)]
        # voices 2x louder than background
        return (2 * audio_array + background) / 3

    def _postprocess(
        self, audio_array: np.ndarray, background_music: bool  # noqa: FBT001
    ) -> (np.ndarray, int):
        """Convert to PCM, optionally resample and fix voice"""
        logger.info("Postprocessing audio")
        sample_rate = SAMPLE_RATE
        if background_music:
            audio_array = self._add_background_music(audio_array)
        if self._cfg.use_voice_fixer:
            audio_array = resample(
                y=audio_array, orig_sr=SAMPLE_RATE, target_sr=OUTPUT_SAMPLE_RATE
            )
            is_cuda = self.tts.device == "cuda"
            audio_array = self.vf.restore_inmem(
                wav_10k=audio_array, cuda=is_cuda, mode=0
            )
            audio_array = audio_array.squeeze()
            sample_rate = OUTPUT_SAMPLE_RATE
        # np.int32 is needed in order for the wav file to end up begin 32bit width
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html#scipy-io-wavfile-write
        audio_array = self._to_pcm(audio_array)
        return audio_array, sample_rate

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

    def _init_models(self):
        """download huggingface hub models from S3 if no local cache"""
        if self._cfg.use_s3_model_cache:
            if not cache_is_present():
                try:
                    download_model_cache()
                except Exception as e:
                    logger.error("Failed to download model cache, continuing", error=e)
            else:
                logger.info("Found local HF hub model cache")
            assert cache_is_present(), "Model cache must be complete"
