import concurrent.futures

import structlog

from wet_toast_talk_radio.common.aws_clients import new_s3_client
from wet_toast_talk_radio.media_store.config import S3Config
from wet_toast_talk_radio.media_store.media_store import ShowId

logger = structlog.get_logger()


class Migrator:
    """Copy all september and october transcoded shows to fallback playlist"""

    SEPTEMBER_PREFIX = "transcoded/2023-09"
    OCTOBER_PREFIX = "transcoded/2023-10"
    TRANSCODED_DIR = "transcoded"
    FALLBACK_DIR = "transcoded/fallback"

    def __init__(self, cfg: S3Config):
        self._cfg = cfg
        if self._cfg.local:
            raise NotImplementedError("Local mode not supported")
        self.s3 = new_s3_client(self._cfg.local)

    def run(self):
        """Copy all transcoded shows to fallback playlist"""
        logger.info("Copying transcoded shows to fallback playlist")
        september = self.list_all_objects(self.SEPTEMBER_PREFIX)
        october = self.list_all_objects(self.OCTOBER_PREFIX)
        objects = september + october
        show_ids = self.objects_to_show_ids(objects)
        # primary sort by date, secondary sort by show_i, to keep order of shows
        show_ids.sort(key=lambda s: s.show_i)
        show_ids.sort(key=lambda s: s.date)

        logger.info("Copying shows", count=len(show_ids))
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._cfg.max_workers
        ) as executor:
            futures = []
            for i, show_id in enumerate(show_ids):
                futures.append(executor.submit(self.copy_show, show_id, i))
            concurrent.futures.wait(futures)

        logger.info("Done copying shows")

    def list_objects(self, continuation_token: str, prefix: str):
        # silly boto3 does not accept None as noop
        return (
            self.s3.list_objects_v2(
                Bucket=self._cfg.bucket_name,
                ContinuationToken=continuation_token,
                Prefix=prefix,
            )
            if continuation_token
            else self.s3.list_objects_v2(Bucket=self._cfg.bucket_name, Prefix=prefix)
        )

    def list_all_objects(self, prefix: str):
        logger.info("Listing objects", prefix=prefix)
        done = False
        continuation_token = None
        objects = []
        while not done:
            response = self.list_objects(
                continuation_token=continuation_token, prefix=prefix
            )
            objects.extend(response["Contents"])
            continuation_token = response.get("NextContinuationToken")
            done = continuation_token is None
        return objects

    @staticmethod
    def objects_to_show_ids(objects: list):
        keys = (obj["Key"] for obj in objects)
        splits = (key.split("/") for key in keys)
        unique_shows = {ShowId(date=s[1], show_i=int(s[2])) for s in splits}
        return list(unique_shows)

    def copy_show(self, show_id: ShowId, i: int):
        logger.info("Copying show", show_id=show_id, i=i)
        metadata = "/".join([self.TRANSCODED_DIR, show_id.store_key(), "metadata.json"])
        show = "/".join([self.TRANSCODED_DIR, show_id.store_key(), "show.mp3"])
        self.copy_object(
            source=metadata,
            target="/".join([self.FALLBACK_DIR, str(i), "metadata.json"]),
        )
        self.copy_object(
            source=show, target="/".join([self.FALLBACK_DIR, str(i), "show.mp3"])
        )

    def copy_object(self, source: str, target: str):
        self.s3.copy_object(
            CopySource=f"{self._cfg.bucket_name}/{source}",
            Bucket=self._cfg.bucket_name,
            Key=target,
        )
