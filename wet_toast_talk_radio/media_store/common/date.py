import http
from datetime import datetime

import requests


def get_current_utc_date() -> datetime:
    """Get the current UTC date from WorldTimeAPI."""
    api_url = "http://worldtimeapi.org/api/ip"
    response = requests.get(api_url)
    if response.status_code == http.HTTPStatus.OK:
        data = response.json()
        datetime_str = data["datetime"]
        now = datetime.fromisoformat(datetime_str).utcnow()
        return now.date()
    else:
        raise Exception("Failed to retrieve current UTC time from WorldTimeAPI")


def get_current_iso_utc_date() -> str:
    """Get the current UTC date from WorldTimeAPI in ISO format."""
    now = get_current_utc_date()
    return now.isoformat()
