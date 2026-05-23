import httpx
import structlog
from typing import Optional

log = structlog.get_logger()

IQAIR_BASE_URL = "http://api.airvisual.com/v2"


async def fetch_city_air_quality(
    city: str,
    state: str,
    country: str,
    api_key: str,
) -> Optional[dict]:
    if api_key == "demo":
        log.warning("iqair_demo_mode", city=city, note="Using mock data — set IQAIR_API_KEY in .env")
        return _mock_air_quality(city)

    url = f"{IQAIR_BASE_URL}/city"
    params = {"city": city, "state": state, "country": country, "key": api_key}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "success":
                log.warning(
                    "iqair_api_non_success",
                    city=city,
                    status=data.get("status"),
                    message=data.get("data", {}).get("message"),
                )
                return None

            pollution = data["data"]["current"]["pollution"]
            result = {
                "aqi": pollution.get("aqius"),
                "pm25": pollution.get("p2", {}).get("conc"),
                "pm10": pollution.get("p1", {}).get("conc"),
            }
            log.info("iqair_fetch_ok", city=city, aqi=result["aqi"])
            return result

        except httpx.HTTPStatusError as exc:
            log.error(
                "iqair_http_error",
                city=city,
                status_code=exc.response.status_code,
                detail=exc.response.text[:200],
            )
            return None
        except httpx.TimeoutException:
            log.error("iqair_timeout", city=city)
            return None
        except httpx.RequestError as exc:
            log.error("iqair_request_error", city=city, error=str(exc))
            return None
        except (KeyError, TypeError) as exc:
            log.error("iqair_parse_error", city=city, error=str(exc))
            return None


# Mock data for demo mode

import random

_MOCK_BASE: dict[str, int] = {
    "Warsaw": 65,
    "Krakow": 90,
    "Berlin": 40,
    "Prague": 55,
    "Vienna": 35,
    "Paris": 60,
    "London": 45,
    "Madrid": 50,
    "Rome": 70,
    "Amsterdam": 38,
}


def _mock_air_quality(city: str) -> dict:
    base_aqi = _MOCK_BASE.get(city, 50)
    aqi = max(1, base_aqi + random.randint(-10, 10))
    return {
        "aqi": aqi,
        "pm25": round(aqi * 0.35 + random.uniform(-2, 2), 1),
        "pm10": round(aqi * 0.55 + random.uniform(-3, 3), 1),
    }
