# Weather Monitor

A FastAPI service that polls [Open-Meteo](https://open-meteo.com/) for current weather in Ottawa, Toronto, and Vancouver, stores readings in SQLite, evaluates alert rules, and exposes readings and notable events through a REST API.

No API key is required for Open-Meteo.

## Cursor setup

The `.cursor` directory customizes Cursor for this project rather than relying on generic AI assistance.

```
.cursor/
  analyze_data.py       # Tools to analyze stored readings and events from SQLite
  rules/
    event_rules.mdc     # Event detection and deduplication requirements
    polling_rules.mdc   # Polling, retries, logging, and storage requirements
  agents/
    event_reviewer.md   # Event Reviewer agent for alert logic review
```

## Monitored cities

| City      | Latitude | Longitude |
|-----------|----------|-----------|
| Ottawa    | 45.42    | -75.69    |
| Toronto   | 43.70    | -79.42    |
| Vancouver | 49.25    | -123.12   |

Data is fetched from:

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}&longitude={lon}
  &current=temperature_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code
  &wind_speed_unit=kmh
  &timezone=auto
```

## API endpoints

| Method | Path        | Description |
|--------|-------------|-------------|
| GET    | `/health`   | Service health check (`status`, `readings_stored`, `events_stored`) |
| GET    | `/readings` | Weather readings (optional `city`, `limit`; default limit 50) |
| GET    | `/events`   | Notable events (optional `city`, `limit`; default limit 50) |

Both list endpoints return the most recent records first and query SQLite on every request.

## Running locally

```bash
pip install -r requirements.txt
python -m app.main
```

The server listens on `http://127.0.0.1:8080`. The background poller runs every **15 minutes**.

Database path defaults to `data/weather.db`. Override with:

```bash
export DB_PATH=/path/to/weather.db   # Linux/macOS
$env:DB_PATH = "path\to\weather.db"  # Windows PowerShell
```

## Docker

```bash
docker compose up --build
```

The `./data` directory is bind-mounted to `/app/data` so the database persists across container restarts.

## Tests

```bash
python -m pytest tests/ -v
```

## CI/CD

On every push to `main`, GitHub Actions runs unit tests and builds the Docker image. See `.github/workflows/ci-cd.yml`.

## How alerting works

- Each city is polled independently; a failure in one city does not stop the others.
- A reading is stored only when its timestamp is **new** for that city (Open-Meteo updates roughly hourly; repeated polls with the same timestamp are skipped).
- Rules run only after a **new** reading is stored.
- The first reading for a city establishes a baseline; no events are emitted until a prior reading exists.
- Events are **edge-triggered**: a rule fires when conditions newly become true, not on every poll while they remain true.

## Event rules (17)

WMO `weather_code` values are used where noted. Full codes: [Open-Meteo documentation](https://open-meteo.com/en/docs).

### City-specific rules

| Rule | City | Alert level | Condition | Notification |
|------|------|-------------|-----------|----------------|
| `vancouver_late_spring_squall` | Vancouver | Yellow Advisory | `weather_code` in 81, 82 and `wind_speed_10m` ≥ 45 km/h | Heavy rain showers and strong winds are hitting Vancouver. Stay off the water and use caution on coastal routes. |
| `toronto_early_heatwave_shock` | Toronto | Orange Warning | `apparent_temperature` ≥ 35°C and `temperature_2m` ≥ 30°C | Humidex is 35°C or higher in Toronto. Limit outdoor activity, stay hydrated, and check on vulnerable neighbours. |
| `ottawa_flash_urban_flood` | Ottawa | Orange Warning | `weather_code` in 65, 82 and `precipitation` ≥ 25 mm | Heavy rain is falling in Ottawa with high accumulation. Avoid flooded roads and watch for basement flooding. |
| `toronto_commuter_flash_freeze` | Toronto | Orange Warning | `weather_code` in 96, 99 and `precipitation` ≥ 15 mm | Hail and heavy rain are hitting Toronto highways. Slow down, increase following distance, and delay non-essential travel. |
| `vancouver_coastal_fog_blindspot` | Vancouver | Yellow Advisory | `weather_code` in 45, 48 and `wind_speed_10m` ≤ 10 km/h | Dense fog with little wind in Vancouver. Allow extra travel time and use extra caution on roads and on the water. |
| `ottawa_stagnant_smog_trap` | Ottawa | Yellow Advisory | `temperature_2m` ≥ 28°C and `wind_speed_10m` ≤ 8 km/h | Heat built up in Ottawa without wind to disperse it. Exercise caution if you have breathing sensitivity. |

### All-city rules

| Rule | Cities | Alert level | Condition | Notification |
|------|--------|-------------|-----------|----------------|
| `severe_microburst_thunderstorm_wind` | Ottawa, Toronto, Vancouver | Orange Warning | `weather_code` in 95, 96, 99 and `wind_speed_10m` ≥ 60 km/h | Thunderstorm winds are dangerously strong. Stay indoors, away from windows, and watch for downed trees or power lines. |
| `close_your_windows_wind` | All | Yellow Advisory | Previous `wind_speed_10m` &lt; 20 and current ≥ 20 km/h | Wind is picking up (≥ 20 km/h). Small branches are moving. It might be time to close your windows. |
| `grill_or_chill_line` | All | Yellow Advisory | `apparent_temperature` ≥ 22°C and `weather_code` in 0, 1, 2 (clear) | Excellent patio weather! Sunny skies and it feels like 22°C or warmer outside. |
| `grab_light_jacket_thermal_drop` | All | Yellow Advisory | `temperature_2m` drops ≥ 4°C within ~1–3 hours vs reading ~3h ago, and current `temperature_2m` ≤ 15°C | Temperature is dropping quickly. It has cooled down by 4°C and is now under 15°C. Grab a sweater or jacket if you are heading out. |
| `incoming_rain_humid_chill` | All | Yellow Advisory | `weather_code` in 51, 61, 80 and `temperature_2m` ≤ 14°C | Light rain or drizzle starting with cool temperatures (under 14°C). An umbrella or waterproof jacket is recommended. |
| `sudden_muggy_shift_indoor_ac` | All | Yellow Advisory | `temperature_2m` ≥ 23°C and `apparent_temperature` ≥ `temperature_2m` + 4°C | Humidity is rising sharply. It feels significantly stickier than the actual air temperature. |

### Cross-city predictive rules

| Rule | Alert city | Alert level | Condition | Notification |
|------|------------|-------------|-----------|----------------|
| `instability_transfer_toronto_to_ottawa` | Ottawa | Internal Predictive Watch | Toronto: thunderstorm codes 95, 96, 99 and `temperature_2m` ≥ 25°C; Ottawa: `temperature_2m` ≥ 22°C | Thunderstorms are active in Toronto with warm conditions in Ottawa. Prepare for severe weather in Ottawa within the next 4 to 5 hours. |
| `continental_heat_pump` | Toronto, Ottawa | System Informational Flag | Vancouver `temperature_2m` ≥ 26°C (newly crossed) | Vancouver is unusually warm. Target city may see a major heat spike in 4 to 5 days—plan ahead for cooling and hydration. |
| `frontal_boundary_flash_flood_trap` | Ottawa | Red Warning | Toronto: rain codes 63, 65 and `wind_speed_10m` ≥ 30 km/h; Ottawa: `precipitation` ≥ 10 mm | Heavy rain is stalled between Toronto and Ottawa. Ottawa faces elevated flash-flood risk. Avoid low-lying areas and basements. |
| `commuter_wind_corridor_toronto_to_ottawa` | Ottawa | Internal Predictive Watch | Toronto `wind_speed_10m` ≥ 25 km/h with increasing trend | Wind is increasing in Toronto along the commuter corridor. Expect a blustery evening in Ottawa in about 4 hours. |
| `rainy_afternoon_shift_toronto_to_ottawa` | Ottawa | Internal Predictive Watch | Toronto clear (`weather_code` 0) after ≥2 rainy morning readings (6 AM–12 PM); Ottawa rain codes 61 or 63 | Toronto cleared after a rainy morning while Ottawa is still seeing rain. Expect Ottawa skies to clear in about 3 to 4 hours. |

## Project layout

```
app/
  main.py           # FastAPI app and routes
  models.py         # Pydantic models
  storage.py        # SQLite persistence
  weather_client.py # Open-Meteo client
  event_rules.py    # Alert rule functions
  poller.py         # Background polling loop
tests/              # Unit tests
data/               # SQLite database (default location)
```
