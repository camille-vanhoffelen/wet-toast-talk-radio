import concurrent.futures
import multiprocessing
import threading
import time
from datetime import timedelta
from typing import Optional

import shout as libshout
import structlog
from pydantic import BaseModel

from wet_toast_talk_radio.common.secret_val import SecretVar
from wet_toast_talk_radio.common.task_log_ctx import task_log_ctx
from wet_toast_talk_radio.disc_jockey.auto_dj import AutoDJ
from wet_toast_talk_radio.media_store.media_store import MediaStore
from wet_toast_talk_radio.message_queue.message_queue import MessageQueue
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator

logger = structlog.get_logger()


class ShoutClientConfig(BaseModel):
    hostname: str = "localhost"
    port: int = 8000
    password: SecretVar[str]
    mount: str = "stream"
    bitrate: int = 128
    samplerate: int = 44100
    channels: int = 1
    user: str = "source"
    protocol: str = "http"  # 'http' | 'xaudiocast' | 'icy'
    public: int = 1
    autodj_key: Optional[SecretVar[str]] = None


def validate_config(cfg: ShoutClientConfig):
    assert cfg is not None, "ShoutClientConfig is None"
    assert cfg.password, "ShoutClientConfig.password is not set"


def init_shout(cfg: ShoutClientConfig) -> libshout.Shout:
    logger.info(f"Using libshout version {libshout.version()}")
    shout = libshout.Shout()
    shout.host = cfg.hostname
    shout.port = cfg.port
    shout.user = cfg.user
    shout.password = cfg.password.value()
    shout.mount = cfg.mount
    shout.format = "vorbis"  # vorbis | mp3
    shout.protocol = cfg.protocol
    shout.name = "Wet Toast Talk Radio"
    shout.genre = "Talk Radio"
    shout.url = "https://wettoast.ai"
    shout.public = cfg.public
    shout.audio_info = {
        libshout.SHOUT_AI_BITRATE: str(cfg.bitrate),
        libshout.SHOUT_AI_SAMPLERATE: str(cfg.samplerate),
        libshout.SHOUT_AI_CHANNELS: str(cfg.channels),
    }

    return shout


@task_log_ctx("shout_client")
class ShoutClient:
    def __init__(
        self,
        cfg: ShoutClientConfig | None,
        media_store: MediaStore,
        message_queue: MessageQueue,
        radio_operator: RadioOperator,
    ):
        validate_config(cfg)
        self._cfg = cfg
        self._media_store = media_store
        self._message_queue = message_queue
        self._processes = []
        self._radio_operator = radio_operator

    def start(self, wait_time: timedelta = timedelta(seconds=1)):
        auto_dj = AutoDJ(self._cfg.autodj_key)

        with concurrent.futures.ProcessPoolExecutor() as executor:
            m = multiprocessing.Manager()
            stream_queue = m.Queue(maxsize=1)
            cancel_event = m.Event()

            futures = []
            futures.append(
                executor.submit(_stream, cancel_event, self._cfg, stream_queue, auto_dj)
            )
            futures.append(
                executor.submit(
                    _prepare,
                    cancel_event,
                    self._message_queue,
                    self._media_store,
                    stream_queue,
                    wait_time,
                )
            )

            res = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_EXCEPTION
            )
            for d in res.done:
                logger.error(
                    "Process exited", result=d.result(), exception=d.exception()
                )
            cancel_event.set()


def _prepare(
    cancel_event: threading.Event,
    message_queue: MessageQueue,
    media_store: MediaStore,
    stream_queue: multiprocessing.Queue,
    wait_time: timedelta = timedelta(seconds=1),
):
    """Check message queue for new shows to stream and add them to the internal stream stream_queue.
    Only add a new show to the internal stream stream_queue if it is empty.
    """
    prepare_logger = logger.bind(process="prepare")
    prepare_logger.info("Starting prepare process")
    try:
        while True:
            if cancel_event.is_set():
                prepare_logger.info("Cancel event set, exiting")
                return

            if not stream_queue.full():
                prepare_logger.info(
                    "Stream queue is not full, waiting for next show..."
                )
                next_show_message = message_queue.get_next_stream_show()
                prepare_logger.info(
                    f"Got next show {next_show_message.show_id}",
                    show_id=next_show_message.show_id,
                )
                next_show_bytes = media_store.get_transcoded_show(
                    next_show_message.show_id
                )
                prepare_logger.info(
                    "Show downloaded", show_id=next_show_message.show_id
                )
                stream_queue.put(
                    (
                        next_show_bytes,
                        next_show_message.show_id,
                    )
                )
                prepare_logger.info(
                    "Show added to stream queue", show_id=next_show_message.show_id
                )
                message_queue.delete_stream_show(next_show_message.receipt_handle)
                prepare_logger.info(
                    "Show deleted from message_queue", show_id=next_show_message.show_id
                )

            time.sleep(wait_time.total_seconds())
    except Exception as e:
        cancel_event.set()
        raise e


_SHOW_CHUNK_SIZE = 4096


# https://github.com/yomguy/python-shout/blob/master/example.py
def _stream(
    cancel_event: threading.Event,
    cfg: ShoutClientConfig,
    stream_queue: multiprocessing.Queue,
    auto_dj: AutoDJ,
    wait_time: timedelta = timedelta(seconds=1),
):
    """Get show from internal stream stream_queue and send it to the shout server in batches."""
    shout = init_shout(cfg)
    stream_logger = logger.bind(process="stream")
    stream_logger.info("Starting stream process")
    try:
        while True:
            if cancel_event.is_set():
                stream_logger.info("Cancel event set, exiting stream process")
                auto_dj.start(stream_logger)
                return

            if stream_queue.empty():
                stream_logger.warn(
                    "Stream queue is empty, waiting to start stream again..."
                )
                time.sleep(wait_time.total_seconds())
                continue

            auto_dj.stop(stream_logger)
            stream_logger.info("Connecting to shout server")
            shout.open()
            shout.get_connected()
            while not stream_queue.empty():
                show_bytes, show_id = stream_queue.get()
                stream_logger.info(f"Playing show {show_id.store_key()}")
                shout.set_metadata({"song": show_id.store_key()})
                for i in range(0, len(show_bytes), _SHOW_CHUNK_SIZE):
                    chunk = show_bytes[i : i + _SHOW_CHUNK_SIZE]
                    shout.send(chunk)
                    shout.sync()

                stream_logger.info(f"Finished playing show {show_id}")
            shout.close()
            auto_dj.start(stream_logger)

    except Exception as e:
        auto_dj.start(stream_logger)
        cancel_event.set()
        raise e
