from typing import Optional

import requests

from wet_toast_talk_radio.common.secret_val import SecretVar


class AutoDJ:
    def __init__(self, key: Optional[SecretVar[str]]):
        self._enabled = False
        if key:
            self._enabled = True
            self._url = "http://voscast.com/api/"
            self._key_param = ("key", key.value())

    def stop(self, logger):
        """Stops the autodj stream on voscast.
        This is needed to allow the shout client to take over the stream.
        """
        if self._enabled:
            logger.info("Stopping audodj...")
            params = [self._key_param, ("action", "stop")]
            resp = requests.get(self._url, params=params, timeout=5)
            if resp.status_code != requests.codes.ok:
                raise Exception("Failed to stop autodj")
            logger.info("Autodj stopped!")

    def start(self, logger):
        """Starts the autodj stream on voscast."""
        if self._enabled:
            logger.info("Starting audodj...")
            params = [self._key_param, ("action", "start")]
            resp = requests.get(self._url, params=params, timeout=5)
            if resp.status_code != requests.codes.ok:
                raise Exception("Failed to start autodj")
            logger.info("Autodj started!")
