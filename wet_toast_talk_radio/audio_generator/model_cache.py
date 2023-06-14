import tarfile
import threading
from pathlib import Path

import boto3
import huggingface_hub
import structlog

logger = structlog.get_logger()

S3_MODEL_CACHE_BUCKET = "wet-toast-model-cache"
S3_MODEL_CACHE_FILE = "model-cache-2023-06-11.tar.gz"
LOCAL_MODEL_CACHE_FILE = ".cache.tar.gz"


def cache_is_present() -> bool:
    """Check if huggingface hub model cache is present"""
    try:
        cache_info = huggingface_hub.scan_cache_dir()
        return bool(cache_info.repos)
    except huggingface_hub.CacheNotFound:
        return False


def download_model_cache():
    """Download model cache from S3 and extract to $HOME/.cache"""
    logger.info(f"Downloading model cache: {S3_MODEL_CACHE_FILE}")
    home_dir = Path(huggingface_hub.constants.default_home).parent.absolute()
    filename = home_dir / LOCAL_MODEL_CACHE_FILE
    # TODO creds
    s3 = boto3.client("s3")
    callback = ProgressPercentage(client=s3, bucket=S3_MODEL_CACHE_BUCKET, filename=S3_MODEL_CACHE_FILE)
    s3.download_file(Bucket=S3_MODEL_CACHE_BUCKET, Key=S3_MODEL_CACHE_FILE, Filename=filename, Callback=callback)
    logger.info("Finished downloading model cache")
    logger.info("Extracting model cache archive")
    with tarfile.open(filename, "r:gz") as f:
        f.extractall(home_dir)
    logger.info("Removing model cache archive")
    filename.unlink()


class ProgressPercentage(object):
    def __init__(self, client, bucket, filename):
        self._filename = filename
        self._size = client.head_object(Bucket=bucket, Key=filename)["ContentLength"]
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
