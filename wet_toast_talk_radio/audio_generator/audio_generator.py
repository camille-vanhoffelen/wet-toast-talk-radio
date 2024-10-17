import json
from pathlib import Path
from typing import Callable

import numpy as np
import structlog
import torch

from wet_toast_talk_radio.audio_generator.config import (
    AudioGeneratorConfig,
    validate_config,
)
from wet_toast_talk_radio.common.dialogue import Line, read_lines
from wet_toast_talk_radio.common.log_ctx import task_log_ctx
from wet_toast_talk_radio.common.path import delete_folder
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowMetadata, ShowName
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue

logger = structlog.get_logger()

SAMPLE_RATE = 24000
SILENCE = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence
LONG_SILENCE = np.zeros(int(1 * SAMPLE_RATE))  # second of silence
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

    def run(
        self,
    ) -> None:
        """Reads script shows from message_queue, generates audio, and uploads to media_store"""
        logger.info("Starting audio generator...")
        assert (
            self._media_store is not None
        ), "MediaStore must be provided to run AudioGenerator"
        assert (
            self._message_queue is not None
        ), "MessageQueue must be provided to run AudioGenerator"

        while script_show_message := self._message_queue.poll_script_show():
            show_id = script_show_message.show_id
            logger.info("Generating audio for script show", show_id=show_id)
            self._media_store.download_script_show(
                show_id=show_id, dir_output=self._script_shows_dir
            )
            self._media_store.download_script_show_metadata(
                show_id=show_id, dir_output=self._script_shows_dir
            )
            script = read_lines(
                self._script_shows_dir / show_id.store_key() / "show.jsonl"
            )
            metadata = read_metadata(
                self._script_shows_dir / show_id.store_key() / "metadata.json"
            )

            def heartbeat():
                self._message_queue.change_message_visibility_timeout(
                    receipt_handle=script_show_message.receipt_handle,
                    timeout_in_s=self._cfg.heartbeat_interval_in_s,
                )

            background_music = bool(metadata.show_name == ShowName.MODERN_MINDFULNESS)
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

    def generate(self, lines: list[Line], output_dir: Path) -> None:
        """Generates audio for lines and saves under output_dir."""
        raise NotImplementedError("AudioGenerator is not implemented")

    def _script_to_audio(
        self,
        lines: list[Line],
        background_music: bool = False,  # noqa: FBT001, FBT002
        sentence_callbacks: list[Callable] | None = None,
    ) -> bytes:
        raise NotImplementedError("AudioGenerator is not implemented")

    def _line_to_audio(
        self,
        line: Line,
        sentence_callbacks: list[Callable] | None,
        voices: dict[str, tuple[torch.Tensor, torch.Tensor]],
    ) -> np.ndarray:
        raise NotImplementedError("AudioGenerator is not implemented")

    @staticmethod
    def _add_background_music(audio_array: np.ndarray) -> np.ndarray:
        """Add background music to audio
        Everything done @ 24 kHz sample rate"""
        raise NotImplementedError("AudioGenerator is not implemented")

    @staticmethod
    def _add_prefix_jingle(audio_array: np.ndarray) -> np.ndarray:
        """Add jingle prefix to audio.
        Everything done @ 24 kHz sample rate"""
        raise NotImplementedError("AudioGenerator is not implemented")

    def _postprocess(
        self, audio_array: np.ndarray, background_music: bool  # noqa: FBT001
    ) -> tuple[np.ndarray, int]:
        """Convert to PCM, optionally resample and fix voice"""
        raise NotImplementedError("AudioGenerator is not implemented")

    def _to_pcm(self, sig, dtype: str = "int32") -> np.ndarray:
        """Convert floating point signal with a range from -1 to 1 to PCM.
        Any signal values outside the interval [-1.0, 1.0) are clipped.
        No dithering is used.
        Note that there are different possibilities for scaling floating
        point numbers to PCM numbers, this function implements just one of
        them.  For an overview of alternatives see
        http://blog.bjornroche.com/2009/12/int-float-int-its-jungle-out-there.html
        """
        raise NotImplementedError("AudioGenerator is not implemented")

    def _init_models(self):
        """download huggingface hub models from S3 if no local cache"""
        raise NotImplementedError("AudioGenerator is not implemented")


def read_metadata(metadata_path: Path):
    if metadata_path.is_file():
        metadata_dict = json.loads(metadata_path.read_text())
        return ShowMetadata(**metadata_dict)
    else:
        # TODO remove, temporary default until all shows have metadata
        return ShowMetadata(ShowName.ADVERTS)
