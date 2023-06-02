from media_store import MediaStore


class S3MediaStore(MediaStore):
    """A cloud  media store where objects are stored to s3"""

    def __init__(self):
        pass

    def upload_raw_show(self):
        """Upload raw show (.wav) to the media store"""

    def download_raw_show(self):
        """Download raw show (.wav) from the media store"""
