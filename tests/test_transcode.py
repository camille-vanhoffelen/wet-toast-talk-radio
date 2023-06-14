from pathlib import Path

import boto3
import pytest

from wet_toast_talk_radio.common.aws_clients import new_s3_client
from wet_toast_talk_radio.disc_jockey import DiscJockey
from wet_toast_talk_radio.disc_jockey.config import (
    DiscJockeyConfig,
    MediaTranscoderConfig,
)
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.config import MediaStoreConfig
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.media_store.s3.config import S3Config

_BUCKET_NAME = "wet-toast-talk-radio"


def _clear_bucket(s3_client: boto3.client):
    response = s3_client.list_objects_v2(Bucket=_BUCKET_NAME)
    if "Contents" in response:
        objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]
        response = s3_client.delete_objects(
            Bucket=_BUCKET_NAME, Delete={"Objects": objects_to_delete}
        )


@pytest.fixture()
def setup_bucket() -> list[ShowId]:
    s3_client = new_s3_client(local=True)
    response = s3_client.list_objects_v2(Bucket=_BUCKET_NAME)
    if "Contents" in response:
        objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]
        response = s3_client.delete_objects(
            Bucket=_BUCKET_NAME, Delete={"Objects": objects_to_delete}
        )

    media_store = new_media_store(
        MediaStoreConfig(s3=S3Config(bucket_name=_BUCKET_NAME, local=True))
    )
    data_dir = (
        Path(__file__).parent.parent / "wet_toast_talk_radio" / "media_store" / "data"
    )
    today = get_current_iso_utc_date()
    ret = []
    i = 0
    for file in data_dir.iterdir():
        if file.is_file() and file.name.endswith(".wav"):
            show = ShowId(i, today)
            with file.open("rb") as f:
                data = f.read()
                media_store.put_raw_show(show, data)
            ret.append(show)
            i += 1
    return ret


class TestTranscode:
    @pytest.mark.integration()
    def test_transcode(self, setup_bucket: list[ShowId]):
        raw_shows = setup_bucket
        media_store = new_media_store(
            MediaStoreConfig(s3=S3Config(bucket_name=_BUCKET_NAME, local=True))
        )
        cfg = DiscJockeyConfig(
            media_transcoder=MediaTranscoderConfig(
                clean_tmp_dir=True,
            )
        )

        dj = DiscJockey(cfg, media_store)
        dj.transcode_latest_media()

        assert len(media_store.list_transcoded_shows()) == len(raw_shows)
