from datetime import datetime, timezone

import pytest

from app.models import WeatherReading
from app.storage import Storage


@pytest.fixture
def storage(tmp_path: pytest.TempPathFactory) -> Storage:
    return Storage(tmp_path / "test.db")


@pytest.fixture
def sample_reading() -> WeatherReading:
    return WeatherReading(
        city="Ottawa",
        timestamp=datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc),
        weather_code=3,
        temperature_2m=15.0,
        apparent_temperature=13.0,
        precipitation=0.0,
        wind_speed_10m=10.0,
    )
