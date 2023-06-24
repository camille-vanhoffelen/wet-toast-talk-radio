import http
from datetime import date, datetime, timedelta

import requests


def get_current_utc_date() -> date:
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


def get_offset_utc_date(offset: timedelta) -> date:
    """Get the current UTC date from WorldTimeAPI."""
    return get_current_utc_date() + offset


def get_offset_iso_utc_date(offset: timedelta) -> str:
    """Get the current UTC date from WorldTimeAPI in ISO format."""
    return get_offset_utc_date(offset=offset).isoformat()
