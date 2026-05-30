from datetime import datetime, timezone
from typing import Any

from app.models import NotableEvent, WeatherReading


def _make_event(
    *,
    city: str,
    rule_name: str,
    alert_level: str,
    message: str,
    reading: WeatherReading,
    triggered_values: dict[str, Any],
    event_timestamp: datetime | None = None,
) -> NotableEvent:
    return NotableEvent(
        city=city,
        timestamp=event_timestamp or datetime.now(timezone.utc),
        rule_name=rule_name,
        alert_level=alert_level,
        message=message,
        reading_timestamp=reading.timestamp,
        triggered_values=triggered_values,
    )


def _newly_triggered(current_met: bool, previous_met: bool) -> bool:
    return current_met and not previous_met


def vancouver_late_spring_squall(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None or current.city != "Vancouver":
        return None

    current_met = current.weather_code in (81, 82) and current.wind_speed_10m >= 45.0
    previous_met = previous.weather_code in (81, 82) and previous.wind_speed_10m >= 45.0
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Vancouver",
        rule_name="vancouver_late_spring_squall",
        alert_level="Yellow Advisory",
        message=(
            "Heavy rain showers and strong winds are hitting Vancouver. "
            "Stay off the water and use caution on coastal routes."
        ),
        reading=current,
        triggered_values={
            "weather_code": current.weather_code,
            "wind_speed_10m": current.wind_speed_10m,
        },
    )


def toronto_early_heatwave_shock(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None or current.city != "Toronto":
        return None

    current_met = (
        current.apparent_temperature >= 35.0 and current.temperature_2m >= 30.0
    )
    previous_met = (
        previous.apparent_temperature >= 35.0 and previous.temperature_2m >= 30.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Toronto",
        rule_name="toronto_early_heatwave_shock",
        alert_level="Orange Warning",
        message=(
            "Humidex is 35°C or higher in Toronto. Limit outdoor activity, "
            "stay hydrated, and check on vulnerable neighbours."
        ),
        reading=current,
        triggered_values={
            "apparent_temperature": current.apparent_temperature,
            "temperature_2m": current.temperature_2m,
        },
    )


def ottawa_flash_urban_flood(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None or current.city != "Ottawa":
        return None

    current_met = (
        current.weather_code in (65, 82) and current.precipitation >= 25.0
    )
    previous_met = (
        previous.weather_code in (65, 82) and previous.precipitation >= 25.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Ottawa",
        rule_name="ottawa_flash_urban_flood",
        alert_level="Orange Warning",
        message=(
            "Heavy rain is falling in Ottawa with high accumulation. "
            "Avoid flooded roads and watch for basement flooding."
        ),
        reading=current,
        triggered_values={
            "weather_code": current.weather_code,
            "precipitation": current.precipitation,
        },
    )


def severe_microburst_thunderstorm_wind(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None:
        return None

    current_met = (
        current.weather_code in (95, 96, 99) and current.wind_speed_10m >= 60.0
    )
    previous_met = (
        previous.weather_code in (95, 96, 99) and previous.wind_speed_10m >= 60.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city=current.city,
        rule_name="severe_microburst_thunderstorm_wind",
        alert_level="Orange Warning",
        message=(
            f"Thunderstorm winds are dangerously strong in {current.city}. "
            "Stay indoors, away from windows, and watch for downed trees or power lines."
        ),
        reading=current,
        triggered_values={
            "weather_code": current.weather_code,
            "wind_speed_10m": current.wind_speed_10m,
        },
    )


def toronto_commuter_flash_freeze(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None or current.city != "Toronto":
        return None

    current_met = (
        current.weather_code in (96, 99) and current.precipitation >= 15.0
    )
    previous_met = (
        previous.weather_code in (96, 99) and previous.precipitation >= 15.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Toronto",
        rule_name="toronto_commuter_flash_freeze",
        alert_level="Orange Warning",
        message=(
            "Hail and heavy rain are hitting Toronto highways. "
            "Slow down, increase following distance, and delay non-essential travel."
        ),
        reading=current,
        triggered_values={
            "weather_code": current.weather_code,
            "precipitation": current.precipitation,
        },
    )


def vancouver_coastal_fog_blindspot(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None or current.city != "Vancouver":
        return None

    current_met = (
        current.weather_code in (45, 48) and current.wind_speed_10m <= 10.0
    )
    previous_met = (
        previous.weather_code in (45, 48) and previous.wind_speed_10m <= 10.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Vancouver",
        rule_name="vancouver_coastal_fog_blindspot",
        alert_level="Yellow Advisory",
        message=(
            "Dense fog with little wind in Vancouver. "
            "Allow extra travel time and use extra caution on roads and on the water."
        ),
        reading=current,
        triggered_values={
            "weather_code": current.weather_code,
            "wind_speed_10m": current.wind_speed_10m,
        },
    )


def ottawa_stagnant_smog_trap(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None or current.city != "Ottawa":
        return None

    current_met = (
        current.temperature_2m >= 28.0 and current.wind_speed_10m <= 8.0
    )
    previous_met = (
        previous.temperature_2m >= 28.0 and previous.wind_speed_10m <= 8.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Ottawa",
        rule_name="ottawa_stagnant_smog_trap",
        alert_level="Yellow Advisory",
        message=(
            "Heat built up in Ottawa without wind to disperse it. "
            "Exercise caution if you have breathing sensitivity."
        ),
        reading=current,
        triggered_values={
            "temperature_2m": current.temperature_2m,
            "wind_speed_10m": current.wind_speed_10m,
        },
    )


def instability_transfer_toronto_to_ottawa(
    toronto: WeatherReading,
    toronto_previous: WeatherReading | None,
    ottawa: WeatherReading,
    ottawa_previous: WeatherReading | None,
) -> NotableEvent | None:
    if toronto_previous is None or ottawa_previous is None:
        return None

    current_met = (
        toronto.weather_code in (95, 96, 99)
        and toronto.temperature_2m >= 25.0
        and ottawa.temperature_2m >= 22.0
    )
    previous_met = (
        toronto_previous.weather_code in (95, 96, 99)
        and toronto_previous.temperature_2m >= 25.0
        and ottawa_previous.temperature_2m >= 22.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Ottawa",
        rule_name="instability_transfer_toronto_to_ottawa",
        alert_level="Internal Predictive Watch",
        message=(
            "Thunderstorms are active in Toronto with warm conditions in Ottawa. "
            "Prepare for severe weather in Ottawa within the next 4 to 5 hours."
        ),
        reading=ottawa,
        triggered_values={
            "toronto_weather_code": toronto.weather_code,
            "toronto_temperature_2m": toronto.temperature_2m,
            "ottawa_temperature_2m": ottawa.temperature_2m,
        },
    )


def continental_heat_pump(
    vancouver: WeatherReading,
    vancouver_previous: WeatherReading | None,
    target: WeatherReading,
) -> NotableEvent | None:
    if vancouver_previous is None or target.city not in ("Toronto", "Ottawa"):
        return None

    current_met = vancouver.temperature_2m >= 26.0
    previous_met = vancouver_previous.temperature_2m >= 26.0
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city=target.city,
        rule_name="continental_heat_pump",
        alert_level="System Informational Flag",
        message=(
            f"Vancouver is unusually warm. {target.city} may see a major heat spike "
            "in 4 to 5 days—plan ahead for cooling and hydration."
        ),
        reading=target,
        triggered_values={
            "vancouver_temperature_2m": vancouver.temperature_2m,
            "flagged_city": target.city,
        },
        event_timestamp=vancouver.timestamp,
    )


def frontal_boundary_flash_flood_trap(
    toronto: WeatherReading,
    toronto_previous: WeatherReading | None,
    ottawa: WeatherReading,
    ottawa_previous: WeatherReading | None,
) -> NotableEvent | None:
    if toronto_previous is None or ottawa_previous is None:
        return None

    current_met = (
        toronto.weather_code in (63, 65)
        and toronto.wind_speed_10m >= 30.0
        and ottawa.precipitation >= 10.0
    )
    previous_met = (
        toronto_previous.weather_code in (63, 65)
        and toronto_previous.wind_speed_10m >= 30.0
        and ottawa_previous.precipitation >= 10.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Ottawa",
        rule_name="frontal_boundary_flash_flood_trap",
        alert_level="Red Warning",
        message=(
            "Heavy rain is stalled between Toronto and Ottawa. "
            "Ottawa faces elevated flash-flood risk. Avoid low-lying areas and basements."
        ),
        reading=ottawa,
        triggered_values={
            "toronto_weather_code": toronto.weather_code,
            "toronto_wind_speed_10m": toronto.wind_speed_10m,
            "ottawa_precipitation": ottawa.precipitation,
        },
    )


MORNING_RAIN_WEATHER_CODES = frozenset({51, 61, 63, 65, 80})


def _thermal_drop_met(
    current: WeatherReading,
    earlier: WeatherReading | None,
    *,
    max_hours: float = 3.0,
    min_hours: float = 1.0,
) -> bool:
    if earlier is None:
        return False

    elapsed_hours = (current.timestamp - earlier.timestamp).total_seconds() / 3600
    if elapsed_hours > max_hours or elapsed_hours < min_hours:
        return False

    return (
        earlier.temperature_2m - current.temperature_2m >= 4.0
        and current.temperature_2m <= 15.0
    )


def _morning_had_rain(readings: list[WeatherReading]) -> bool:
    morning_readings = [
        reading for reading in readings if 6 <= reading.timestamp.hour < 12
    ]
    if len(morning_readings) < 2:
        return False

    rainy_readings = sum(
        1
        for reading in morning_readings
        if reading.weather_code in MORNING_RAIN_WEATHER_CODES
        or reading.precipitation > 0.0
    )
    return rainy_readings >= 2


def close_your_windows_wind(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None:
        return None

    if not (
        previous.wind_speed_10m < 20.0 and current.wind_speed_10m >= 20.0
    ):
        return None

    return _make_event(
        city=current.city,
        rule_name="close_your_windows_wind",
        alert_level="Yellow Advisory",
        message=(
            "Wind is picking up (≥ 20 km/h). Small branches are moving. "
            "It might be time to close your windows."
        ),
        reading=current,
        triggered_values={
            "wind_speed_10m": current.wind_speed_10m,
            "previous_wind_speed_10m": previous.wind_speed_10m,
        },
    )


def grill_or_chill_line(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None:
        return None

    current_met = (
        current.apparent_temperature >= 22.0 and current.weather_code in (0, 1, 2)
    )
    previous_met = (
        previous.apparent_temperature >= 22.0 and previous.weather_code in (0, 1, 2)
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city=current.city,
        rule_name="grill_or_chill_line",
        alert_level="Yellow Advisory",
        message=(
            "Excellent patio weather! Sunny skies and it feels like 22°C or warmer outside."
        ),
        reading=current,
        triggered_values={
            "apparent_temperature": current.apparent_temperature,
            "weather_code": current.weather_code,
        },
    )


def grab_light_jacket_thermal_drop(
    current: WeatherReading,
    previous: WeatherReading | None,
    reading_three_hours_ago: WeatherReading | None,
    previous_three_hours_ago: WeatherReading | None = None,
) -> NotableEvent | None:
    if previous is None:
        return None

    current_met = _thermal_drop_met(current, reading_three_hours_ago)
    previous_met = _thermal_drop_met(previous, previous_three_hours_ago)
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city=current.city,
        rule_name="grab_light_jacket_thermal_drop",
        alert_level="Yellow Advisory",
        message=(
            "Temperature is dropping quickly. It has cooled down by 4°C and is now under "
            "15°C. Grab a sweater or jacket if you are heading out."
        ),
        reading=current,
        triggered_values={
            "temperature_2m": current.temperature_2m,
            "earlier_temperature_2m": reading_three_hours_ago.temperature_2m
            if reading_three_hours_ago
            else None,
        },
    )


def incoming_rain_humid_chill(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None:
        return None

    current_met = (
        current.weather_code in (51, 61, 80) and current.temperature_2m <= 14.0
    )
    previous_met = (
        previous.weather_code in (51, 61, 80) and previous.temperature_2m <= 14.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city=current.city,
        rule_name="incoming_rain_humid_chill",
        alert_level="Yellow Advisory",
        message=(
            "Light rain or drizzle starting with cool temperatures (under 14°C). "
            "An umbrella or waterproof jacket is recommended."
        ),
        reading=current,
        triggered_values={
            "weather_code": current.weather_code,
            "temperature_2m": current.temperature_2m,
        },
    )


def sudden_muggy_shift_indoor_ac(
    current: WeatherReading,
    previous: WeatherReading | None,
) -> NotableEvent | None:
    if previous is None:
        return None

    current_met = (
        current.temperature_2m >= 23.0
        and current.apparent_temperature >= current.temperature_2m + 4.0
    )
    previous_met = (
        previous.temperature_2m >= 23.0
        and previous.apparent_temperature >= previous.temperature_2m + 4.0
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city=current.city,
        rule_name="sudden_muggy_shift_indoor_ac",
        alert_level="Yellow Advisory",
        message=(
            "Humidity is rising sharply. It feels significantly stickier than the actual "
            "air temperature."
        ),
        reading=current,
        triggered_values={
            "temperature_2m": current.temperature_2m,
            "apparent_temperature": current.apparent_temperature,
        },
    )


def commuter_wind_corridor_toronto_to_ottawa(
    toronto: WeatherReading,
    toronto_previous: WeatherReading | None,
    toronto_before_previous: WeatherReading | None,
    ottawa: WeatherReading,
) -> NotableEvent | None:
    if toronto_previous is None or toronto_before_previous is None:
        return None

    current_met = (
        toronto.wind_speed_10m >= 25.0
        and toronto.wind_speed_10m > toronto_previous.wind_speed_10m
    )
    previous_met = (
        toronto_previous.wind_speed_10m >= 25.0
        and toronto_previous.wind_speed_10m > toronto_before_previous.wind_speed_10m
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Ottawa",
        rule_name="commuter_wind_corridor_toronto_to_ottawa",
        alert_level="Internal Predictive Watch",
        message=(
            "Wind is increasing in Toronto along the commuter corridor. Expect a blustery "
            "evening in Ottawa in about 4 hours."
        ),
        reading=ottawa,
        triggered_values={
            "toronto_wind_speed_10m": toronto.wind_speed_10m,
            "previous_toronto_wind_speed_10m": toronto_previous.wind_speed_10m,
        },
    )


def rainy_afternoon_shift_toronto_to_ottawa(
    toronto: WeatherReading,
    toronto_previous: WeatherReading | None,
    toronto_morning_readings: list[WeatherReading],
    ottawa: WeatherReading,
    ottawa_previous: WeatherReading | None,
    toronto_previous_morning_readings: list[WeatherReading] | None = None,
) -> NotableEvent | None:
    if toronto_previous is None or ottawa_previous is None:
        return None

    if toronto_previous_morning_readings is None:
        toronto_previous_morning_readings = toronto_morning_readings

    current_met = (
        toronto.weather_code == 0
        and toronto.timestamp.hour >= 12
        and _morning_had_rain(toronto_morning_readings)
        and ottawa.weather_code in (61, 63)
    )
    previous_met = (
        toronto_previous.weather_code == 0
        and toronto_previous.timestamp.hour >= 12
        and _morning_had_rain(toronto_previous_morning_readings)
        and ottawa_previous.weather_code in (61, 63)
    )
    if not _newly_triggered(current_met, previous_met):
        return None

    return _make_event(
        city="Ottawa",
        rule_name="rainy_afternoon_shift_toronto_to_ottawa",
        alert_level="Internal Predictive Watch",
        message=(
            "Toronto cleared after a rainy morning while Ottawa is still seeing rain. "
            "Expect Ottawa skies to clear in about 3 to 4 hours."
        ),
        reading=ottawa,
        triggered_values={
            "toronto_weather_code": toronto.weather_code,
            "ottawa_weather_code": ottawa.weather_code,
        },
    )
