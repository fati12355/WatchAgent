from datetime import datetime, timezone

from app.event_rules import ottawa_stagnant_smog_trap
from app.models import WeatherReading


def test_event_rule_emits_only_when_conditions_newly_triggered():
    previous = WeatherReading(
        city="Ottawa",
        timestamp=datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc),
        weather_code=3,
        temperature_2m=25.0,
        apparent_temperature=24.0,
        precipitation=0.0,
        wind_speed_10m=10.0,
    )
    current = previous.model_copy(
        update={
            "timestamp": datetime(2026, 6, 1, 13, 0, tzinfo=timezone.utc),
            "temperature_2m": 30.0,
            "wind_speed_10m": 5.0,
        }
    )

    assert ottawa_stagnant_smog_trap(current, None) is None
    assert ottawa_stagnant_smog_trap(current, previous) is not None
    assert ottawa_stagnant_smog_trap(current, current) is None
