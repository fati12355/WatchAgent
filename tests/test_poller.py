from datetime import datetime, timezone
from unittest.mock import patch

from app.models import WeatherReading
from app.poller import poll_city


def test_poll_city_skips_reading_when_timestamp_unchanged(storage):
    reading = WeatherReading(
        city="Toronto",
        timestamp=datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc),
        weather_code=3,
        temperature_2m=22.0,
        apparent_temperature=21.0,
        precipitation=0.0,
        wind_speed_10m=12.0,
    )

    with patch("app.poller.fetch_current_weather", return_value=reading):
        assert poll_city(storage, "Toronto") is not None
        assert poll_city(storage, "Toronto") is None

    assert len(storage.list_readings(city="Toronto")) == 1
