import multiprocessing
import time
from datetime import timedelta

import shout as libshout
import structlog
from pydantic import BaseModel

from wet_toast_talk_radio.common.secret_val import SecretVar
from wet_toast_talk_radio.media_store.media_store import MediaStore
from wet_toast_talk_radio.message_queue.message_queue import StreamMQ

logger = structlog.get_logger()


class ShoutClientConfig(BaseModel):
    hostname: str = "localhost"
    port: int = 8000
    password: SecretVar[str]
    mount: str = "/wettoast.ogg"
    bitrate: int = 128
    samplerate: int = 44100
    channels: int = 1
    user: str = "source"
    protocol: str = "http"  # 'http' | 'xaudiocast' | 'icy'
    public: int = 1


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


class ShoutClient:
    def __init__(
        self,
        cfg: ShoutClientConfig | None,
        media_store: MediaStore,
        message_queue: StreamMQ,
    ):
        validate_config(cfg)
        self._cfg = cfg
        self._media_store = media_store
        self._message_queue = message_queue
        self._processes = []

    def start(self, wait_time: timedelta = timedelta(seconds=1)):
        stream_queue = multiprocessing.Queue(maxsize=1)

        stream_process = multiprocessing.Process(
            target=_stream, args=(self._cfg, stream_queue)
        )
        stream_process.start()

        prepare_process = multiprocessing.Process(
            target=_prepare,
            args=(self._message_queue, self._media_store, stream_queue, wait_time),
        )
        prepare_process.start()

        stream_process.join()
        prepare_process.join()


def _prepare(
    message_queue: StreamMQ,
    media_store: MediaStore,
    stream_queue: multiprocessing.Queue,
    wait_time: timedelta = timedelta(seconds=1),
):
    """Check message queue for new shows to stream and add them to the internal stream stream_queue.
    Only add a new show to the internal stream stream_queue if it is empty.
    """
    prepare_logger = logger.bind(process="prepare")
    prepare_logger.info("Starting prepare process")
    while True:
        if not stream_queue.full():
            prepare_logger.info("Stream queue is not full, waiting for next show...")
            next_show_message = message_queue.get_next_stream_show()
            prepare_logger.info(
                f"Got next show {next_show_message.show_id}",
                show_id=next_show_message.show_id,
            )
            next_show_bytes = media_store.get_transcoded_show(next_show_message.show_id)
            prepare_logger.info("Show downloaded", show_id=next_show_message.show_id)
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


_SHOW_CHUNK_SIZE = 4096


# https://github.com/yomguy/python-shout/blob/master/example.py
def _stream(
    cfg: ShoutClientConfig,
    stream_queue: multiprocessing.Queue,
    wait_time: timedelta = timedelta(seconds=1),
):
    """Get show from internal stream stream_queue and send it to the shout server in batches."""
    shout = init_shout(cfg)
    stream_logger = logger.bind(process="stream")
    stream_logger.info("Starting stream process")

    while True:
        if stream_queue.empty():
            stream_logger.warn(
                "Stream queue is empty, waiting to start stream again..."
            )
            time.sleep(wait_time.total_seconds())
            continue
        try:
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
        finally:
            stream_logger.info("Closing shout server connection")
            shout.close()
