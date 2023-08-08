from pathlib import Path

import pytest

from wet_toast_talk_radio.audio_generator.cache import (
    cache_is_present,
    download_model_cache,
)

TEST_S3_MODEL_CACHE_BUCKET = "wet-toast-test-model-cache"
TEST_S3_MODEL_CACHE_KEY = "test-model-cache-2023-08-09.tar"
REPO_ID = "test"
NB_FILES = 2


class TestModelCache:
    @pytest.mark.integration()
    def test_load_s3_model_cache(self, tmp_path: Path):
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        download_model_cache(
            bucket=TEST_S3_MODEL_CACHE_BUCKET,
            key=TEST_S3_MODEL_CACHE_KEY,
            home_dir=home_dir,
        )
        cache_dir = home_dir / ".cache"
        assert cache_is_present(cache_dir=cache_dir)
