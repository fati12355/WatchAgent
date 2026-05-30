import asyncio
import logging
from collections.abc import Callable

from app import event_rules
from app.models import NotableEvent, WeatherReading
from app.storage import Storage
from app.weather_client import CITIES, fetch_current_weather

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 900

SingleCityRule = Callable[[WeatherReading, WeatherReading | None], NotableEvent | None]

SINGLE_CITY_RULES: dict[str, list[SingleCityRule]] = {
    "Vancouver": [
        event_rules.vancouver_late_spring_squall,
        event_rules.vancouver_coastal_fog_blindspot,
    ],
    "Toronto": [
        event_rules.toronto_early_heatwave_shock,
        event_rules.toronto_commuter_flash_freeze,
    ],
    "Ottawa": [
        event_rules.ottawa_flash_urban_flood,
        event_rules.ottawa_stagnant_smog_trap,
    ],
}

ALL_CITY_LIFESTYLE_RULES: list[SingleCityRule] = [
    event_rules.close_your_windows_wind,
    event_rules.grill_or_chill_line,
    event_rules.incoming_rain_humid_chill,
    event_rules.sudden_muggy_shift_indoor_ac,
]


def poll_city(storage: Storage, city: str) -> WeatherReading | None:
    try:
        reading = fetch_current_weather(city)
        if reading is None:
            return None

        latest = storage.get_latest_reading(city)
        if latest is not None and latest.timestamp == reading.timestamp:
            return None

        if not storage.save_reading(reading):
            return None

        logger.info("Stored new reading for %s at %s", city, reading.timestamp)
        return reading
    except Exception as exc:
        logger.warning(
            "Poll failed for %s: %s",
            city,
            type(exc).__name__,
        )
        return None


def evaluate_single_city_rules(
    storage: Storage,
    city: str,
    current: WeatherReading,
) -> list[NotableEvent]:
    previous = storage.get_reading_before(city, current.timestamp)
    events: list[NotableEvent] = []

    for rule in SINGLE_CITY_RULES.get(city, []):
        event = rule(current, previous)
        if event is not None:
            events.append(event)

    for rule in ALL_CITY_LIFESTYLE_RULES:
        event = rule(current, previous)
        if event is not None:
            events.append(event)

    event = event_rules.severe_microburst_thunderstorm_wind(current, previous)
    if event is not None:
        events.append(event)

    reading_three_hours_ago = storage.get_reading_near_hours_before(
        city, current.timestamp, 3.0
    )
    previous_three_hours_ago = (
        storage.get_reading_near_hours_before(city, previous.timestamp, 3.0)
        if previous is not None
        else None
    )
    event = event_rules.grab_light_jacket_thermal_drop(
        current,
        previous,
        reading_three_hours_ago,
        previous_three_hours_ago,
    )
    if event is not None:
        events.append(event)

    return events


def evaluate_cross_city_rules(storage: Storage) -> list[NotableEvent]:
    toronto = storage.get_latest_reading("Toronto")
    ottawa = storage.get_latest_reading("Ottawa")
    vancouver = storage.get_latest_reading("Vancouver")

    if toronto is None or ottawa is None or vancouver is None:
        return []

    toronto_previous = storage.get_reading_before("Toronto", toronto.timestamp)
    ottawa_previous = storage.get_reading_before("Ottawa", ottawa.timestamp)
    vancouver_previous = storage.get_reading_before("Vancouver", vancouver.timestamp)

    events: list[NotableEvent] = []

    event = event_rules.instability_transfer_toronto_to_ottawa(
        toronto,
        toronto_previous,
        ottawa,
        ottawa_previous,
    )
    if event is not None:
        events.append(event)

    for target in (toronto, ottawa):
        event = event_rules.continental_heat_pump(
            vancouver,
            vancouver_previous,
            target,
        )
        if event is not None:
            events.append(event)

    event = event_rules.frontal_boundary_flash_flood_trap(
        toronto,
        toronto_previous,
        ottawa,
        ottawa_previous,
    )
    if event is not None:
        events.append(event)

    toronto_before_previous = storage.get_reading_before(
        "Toronto", toronto_previous.timestamp
    )
    event = event_rules.commuter_wind_corridor_toronto_to_ottawa(
        toronto,
        toronto_previous,
        toronto_before_previous,
        ottawa,
    )
    if event is not None:
        events.append(event)

    morning_start = toronto.timestamp.replace(hour=6, minute=0, second=0, microsecond=0)
    toronto_morning_readings = storage.list_readings_in_range(
        "Toronto",
        morning_start,
        toronto.timestamp,
    )
    toronto_previous_morning_readings = (
        storage.list_readings_in_range(
            "Toronto",
            morning_start,
            toronto_previous.timestamp,
        )
        if toronto_previous is not None
        else []
    )
    event = event_rules.rainy_afternoon_shift_toronto_to_ottawa(
        toronto,
        toronto_previous,
        toronto_morning_readings,
        ottawa,
        ottawa_previous,
        toronto_previous_morning_readings,
    )
    if event is not None:
        events.append(event)

    return events


def run_poll_cycle(storage: Storage) -> None:
    new_readings: dict[str, WeatherReading] = {}

    for city in CITIES:
        reading = poll_city(storage, city)
        if reading is not None:
            new_readings[city] = reading

    if not new_readings:
        return

    for city, reading in new_readings.items():
        for event in evaluate_single_city_rules(storage, city, reading):
            storage.save_event(event)
            logger.info(
                "Stored event %s for %s",
                event.rule_name,
                event.city,
            )

    for event in evaluate_cross_city_rules(storage):
        storage.save_event(event)
        logger.info(
            "Stored event %s for %s",
            event.rule_name,
            event.city,
        )


async def poller_loop(
    storage: Storage,
    interval_seconds: int = POLL_INTERVAL_SECONDS,
) -> None:
    while True:
        try:
            await asyncio.to_thread(run_poll_cycle, storage)
        except Exception as exc:
            logger.exception("Poll cycle failed: %s", type(exc).__name__)
        await asyncio.sleep(interval_seconds)
