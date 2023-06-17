from pathlib import Path

import huggingface_hub
import pytest

from wet_toast_talk_radio.audio_generator.model_cache import (
    cache_is_present,
    download_model_cache,
)

TEST_S3_MODEL_CACHE_BUCKET = "wet-toast-test-model-cache"
TEST_S3_MODEL_CACHE_KEY = "test-model-cache-2023-06-16.tar.gz"
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
        cache_dir = home_dir / ".cache" / "huggingface" / "hub"
        assert cache_is_present(cache_dir=cache_dir)
        cache_info = huggingface_hub.scan_cache_dir(cache_dir=cache_dir)
        assert len(cache_info.repos) == 1
        repo = list(cache_info.repos)[0]
        assert repo.repo_id == REPO_ID
        assert repo.nb_files == NB_FILES
