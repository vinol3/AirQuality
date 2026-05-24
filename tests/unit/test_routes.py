from datetime import datetime, timezone
from app.models.air_quality import AirQualityReading
from app.models.weather import WeatherReading


class TestCitiesRoute:
    def test_list_cities_empty(self, client):
        resp = client.get("/api/v1/cities/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_cities_returns_seeded(self, client, sample_city):
        resp = client.get("/api/v1/cities/")
        assert resp.status_code == 200
        names = [c["name"] for c in resp.json()]
        assert sample_city.name in names

    def test_get_city_exists(self, client, sample_city):
        resp = client.get(f"/api/v1/cities/{sample_city.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["city"]["name"] == sample_city.name

    def test_get_city_not_found(self, client):
        resp = client.get("/api/v1/cities/999999")
        assert resp.status_code == 404


class TestAirQualityRoute:
    def test_air_quality_empty_window(self, client, sample_city):
        resp = client.get(f"/api/v1/cities/{sample_city.id}/air-quality")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_air_quality_with_data(self, client, db, sample_city):
        db.add(AirQualityReading(
            city_id=sample_city.id,
            aqi=75,
            pm25=18.0,
            pm10=28.0,
            recorded_at=datetime.now(tz=timezone.utc),
            source="iqair",
        ))
        db.flush()

        resp = client.get(f"/api/v1/cities/{sample_city.id}/air-quality?hours=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["aqi"] == 75


class TestWeatherRoute:
    def test_weather_empty_window(self, client, sample_city):
        resp = client.get(f"/api/v1/cities/{sample_city.id}/weather")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_weather_with_data(self, client, db, sample_city):
        db.add(WeatherReading(
            city_id=sample_city.id,
            temperature=18.5,
            humidity=65,
            wind_speed=4.0,
            pressure=1013,
            recorded_at=datetime.now(tz=timezone.utc),
            source="openweathermap",
        ))
        db.flush()

        resp = client.get(f"/api/v1/cities/{sample_city.id}/weather?hours=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["temperature"] == 18.5


class TestRankingsRoute:
    def test_rankings_returns_list(self, client):
        resp = client.get("/api/v1/rankings/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_ranking_limit_respected(self, client, sample_city):
        resp = client.get("/api/v1/rankings/?limit=1")
        assert resp.status_code == 200
        assert len(resp.json()) <= 1


class TestHealthRoute:
    def test_health_ok(self, client):
        resp = client.get("/api/v1/admin/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("ok", "degraded")
        assert "db_ok" in data
