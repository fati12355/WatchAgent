from datetime import datetime, timezone

from app.models import WeatherReading


def test_save_reading_rejects_duplicate_city_timestamp(storage, sample_reading):
    assert storage.save_reading(sample_reading) is True
    assert storage.save_reading(sample_reading) is False
    assert len(storage.list_readings(city="Ottawa")) == 1
