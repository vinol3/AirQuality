import pytest
from app.processing.normaliser import (
    normalise_air_quality,
    normalise_weather,
    aqi_to_category,
    aqi_to_color,
)


class TestNormaliseAirQuality:
    def test_valid_input_returns_reading(self):
        raw = {"aqi": 55, "pm25": 12.5, "pm10": 22.0}
        result = normalise_air_quality(city_id=1, raw=raw)
        assert result is not None
        assert result.aqi == 55
        assert result.pm25 == 12.5
        assert result.pm10 == 22.0
        assert result.city_id == 1
        assert result.source == "iqair"

    def test_missing_aqi_returns_none(self):
        """AQI is required — without it we cannot store a meaningful reading."""
        raw = {"aqi": None, "pm25": 12.5}
        result = normalise_air_quality(city_id=1, raw=raw)
        assert result is None

    def test_aqi_out_of_range_returns_none(self):
        raw = {"aqi": 600}  # US AQI max is 500
        result = normalise_air_quality(city_id=1, raw=raw)
        assert result is None

    def test_negative_aqi_returns_none(self):
        raw = {"aqi": -5}
        result = normalise_air_quality(city_id=1, raw=raw)
        assert result is None

    def test_string_aqi_is_coerced(self):
        """API sometimes returns numbers as strings."""
        raw = {"aqi": "75", "pm25": "18.0"}
        result = normalise_air_quality(city_id=1, raw=raw)
        assert result is not None
        assert result.aqi == 75
        assert result.pm25 == 18.0

    def test_pm_values_are_optional(self):
        raw = {"aqi": 42}
        result = normalise_air_quality(city_id=1, raw=raw)
        assert result is not None
        assert result.pm25 is None
        assert result.pm10 is None

    def test_aqi_boundary_values(self):
        for aqi in [0, 1, 499, 500]:
            raw = {"aqi": aqi}
            result = normalise_air_quality(city_id=1, raw=raw)
            assert result is not None, f"Expected valid reading for aqi={aqi}"


class TestNormaliseWeather:
    def test_valid_input_returns_reading(self):
        raw = {"temperature": 15.5, "humidity": 70, "wind_speed": 4.2, "pressure": 1013, "description": "clear"}
        result = normalise_weather(city_id=2, raw=raw)
        assert result is not None
        assert result.temperature == 15.5
        assert result.humidity == 70
        assert result.source == "openweathermap"

    def test_missing_temperature_returns_none(self):
        raw = {"temperature": None, "humidity": 60}
        result = normalise_weather(city_id=2, raw=raw)
        assert result is None

    def test_unrealistic_temperature_clamped(self):
        raw = {"temperature": 200.0, "humidity": 60}  # way above 60°C max
        result = normalise_weather(city_id=2, raw=raw)
        assert result is None

    def test_humidity_optional(self):
        raw = {"temperature": 20.0}
        result = normalise_weather(city_id=2, raw=raw)
        assert result is not None
        assert result.humidity is None


class TestAqiToCategory:
    @pytest.mark.parametrize("aqi,expected", [
        (0,   "Good"),
        (50,  "Good"),
        (51,  "Moderate"),
        (100, "Moderate"),
        (101, "Unhealthy for Sensitive Groups"),
        (150, "Unhealthy for Sensitive Groups"),
        (151, "Unhealthy"),
        (200, "Unhealthy"),
        (201, "Very Unhealthy"),
        (300, "Very Unhealthy"),
        (301, "Hazardous"),
        (None, "Unknown"),
    ])
    def test_categories(self, aqi, expected):
        assert aqi_to_category(aqi) == expected


class TestAqiToColor:
    def test_good_is_green(self):
        assert aqi_to_color(25) == "#4caf50"

    def test_none_is_grey(self):
        assert aqi_to_color(None) == "#9e9e9e"

    def test_hazardous_is_dark_purple(self):
        assert aqi_to_color(400) == "#7b1fa2"
