import tarfile
import threading
from pathlib import Path

import boto3
import structlog

logger = structlog.get_logger()

S3_MODEL_CACHE_BUCKET = "wet-toast-model-cache"
S3_MODEL_CACHE_KEY = "model-cache-2023-08-08.tar"
LOCAL_MODEL_CACHE_FILE = ".cache.tar"
DEFAULT_MODEL_CACHE_PATH = Path.home() / ".cache"
MANDATORY_MODEL_CACHE_FILES = ["tortoise", "voicefixer", "background.wav", "jingle.wav"]
BACKGROUND_PATH = DEFAULT_MODEL_CACHE_PATH / "background.wav"
JINGLE_PATH = DEFAULT_MODEL_CACHE_PATH / "jingle.wav"


def cache_is_present(cache_dir: str | Path | None = None) -> bool:
    """Check if tortoise and voicefixer model caches are present"""
    if not cache_dir:
        cache_dir = DEFAULT_MODEL_CACHE_PATH
    cache_files = list(cache_dir.iterdir())
    cache_file_names = [f.name for f in cache_files]
    return all(f in cache_file_names for f in MANDATORY_MODEL_CACHE_FILES)


def download_model_cache(
    bucket: str = S3_MODEL_CACHE_BUCKET,
    key: str = S3_MODEL_CACHE_KEY,
    home_dir: Path | None = None,
):
    """Download model cache from S3 and extract to $HOME/.cache"""
    logger.info("Initializing boto3 session")
    session = boto3.Session()

    logger.info(f"Downloading model cache: {key}")
    if not home_dir:
        home_dir = Path.home()
    model_cache_archive = home_dir / LOCAL_MODEL_CACHE_FILE
    s3 = session.client("s3")
    callback = ProgressPercentage(client=s3, bucket=bucket, key=key)
    s3.download_file(
        Bucket=bucket, Key=key, Filename=model_cache_archive, Callback=callback
    )
    logger.info("Finished downloading model cache")
    logger.info("Extracting model cache archive")
    with tarfile.open(model_cache_archive, "r") as f:
        f.extractall(home_dir)
    logger.info("Removing model cache archive")
    model_cache_archive.unlink()


class ProgressPercentage(object):
    """Report download progress to logger every 10%"""

    def __init__(self, client, bucket: str, key: str):
        self._key = key
        self._size = client.head_object(Bucket=bucket, Key=key)["ContentLength"]
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._last_percentage = 0

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = self._truncated_percentage(self._seen_so_far, self._size)
            if percentage != self._last_percentage:
                logger.info("Percentage complete", percentage=f"{percentage}%")
                self._last_percentage = percentage

    @staticmethod
    def _truncated_percentage(seen_so_far: float, total_size: float):
        """Return percentage truncated to 1 decimal place"""
        truncated = float("%.1f" % (seen_so_far / total_size))
        return truncated * 100
