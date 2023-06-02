from media_store import MediaStore


class VirtualMediaStore(MediaStore):
    """A local virtual media store where objects are stored in a file on disk"""

    def __init__(self):
        pass

    def upload_raw_show(self):
        """Upload raw show (.wav) to the media store"""

    def download_raw_show(self):
        """Download raw show (.wav) from the media store"""
