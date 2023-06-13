from wet_toast_talk_radio.media_store.common.date import (
    get_current_iso_utc_date,
    get_current_utc_date,
)


class TestDate:
    def test_get_current_utc_date(self):
        today = get_current_utc_date()
        assert today is not None

    def test_get_current_iso_utc_date(self):
        today = get_current_iso_utc_date()
        assert today is not None
