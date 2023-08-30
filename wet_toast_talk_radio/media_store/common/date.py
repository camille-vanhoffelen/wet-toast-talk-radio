import http
from datetime import date, datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def get_current_utc_date() -> date:
    """Get the current UTC date from WorldTimeAPI."""
    retry_strategy = Retry(
        total=10,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    api_url = "http://worldtimeapi.org/api/ip"
    response = session.get(api_url)
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
