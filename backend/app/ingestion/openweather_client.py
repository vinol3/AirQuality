import httpx
import structlog
from typing import Optional

log = structlog.get_logger()

OW_BASE_URL = "https://api.openweathermap.org/data/2.5"


async def fetch_city_weather(
    lat: float,
    lon: float,
    api_key: str,
    city_name: str = "",
) -> Optional[dict]:
    if api_key == "demo":
        log.warning(
            "openweather_demo_mode",
            city=city_name,
            note="Using mock data — set OPENWEATHER_API_KEY in .env",
        )
        return _mock_weather(city_name)

    url = f"{OW_BASE_URL}/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            result = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"],
                "description": (
                    data["weather"][0]["description"] if data.get("weather") else None
                ),
            }
            log.info(
                "openweather_fetch_ok",
                city=city_name,
                temp=result["temperature"],
                humidity=result["humidity"],
            )
            return result

        except httpx.HTTPStatusError as exc:
            log.error(
                "openweather_http_error",
                city=city_name,
                status_code=exc.response.status_code,
                detail=exc.response.text[:200],
            )
            return None
        except httpx.TimeoutException:
            log.error("openweather_timeout", city=city_name)
            return None
        except httpx.RequestError as exc:
            log.error("openweather_request_error", city=city_name, error=str(exc))
            return None
        except (KeyError, TypeError) as exc:
            log.error("openweather_parse_error", city=city_name, error=str(exc))
            return None


# Mock data for demo/dev mode

import random

_MOCK_WEATHER: dict[str, dict] = {
    "Warsaw":    {"temperature": 12.0, "humidity": 70, "wind_speed": 4.5, "pressure": 1013},
    "Krakow":    {"temperature": 11.0, "humidity": 75, "wind_speed": 3.0, "pressure": 1010},
    "Berlin":    {"temperature": 14.0, "humidity": 65, "wind_speed": 5.0, "pressure": 1015},
    "Prague":    {"temperature": 13.0, "humidity": 68, "wind_speed": 3.5, "pressure": 1012},
    "Vienna":    {"temperature": 15.0, "humidity": 60, "wind_speed": 4.0, "pressure": 1014},
    "Paris":     {"temperature": 16.0, "humidity": 63, "wind_speed": 5.5, "pressure": 1011},
    "London":    {"temperature": 13.0, "humidity": 78, "wind_speed": 6.0, "pressure": 1008},
    "Madrid":    {"temperature": 20.0, "humidity": 45, "wind_speed": 3.5, "pressure": 1016},
    "Rome":      {"temperature": 19.0, "humidity": 55, "wind_speed": 2.5, "pressure": 1013},
    "Amsterdam": {"temperature": 12.0, "humidity": 80, "wind_speed": 7.0, "pressure": 1007},
}

_DESCRIPTIONS = ["clear sky", "few clouds", "light rain", "overcast clouds", "moderate rain"]


def _mock_weather(city: str) -> dict:
    base = _MOCK_WEATHER.get(city, {"temperature": 15.0, "humidity": 65, "wind_speed": 4.0, "pressure": 1013})
    return {
        "temperature": round(base["temperature"] + random.uniform(-2, 2), 1),
        "humidity": max(0, min(100, base["humidity"] + random.randint(-5, 5))),
        "wind_speed": round(max(0.0, base["wind_speed"] + random.uniform(-1, 1)), 1),
        "pressure": base["pressure"] + random.randint(-3, 3),
        "description": random.choice(_DESCRIPTIONS),
    }
