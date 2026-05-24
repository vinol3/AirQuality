import random
from locust import HttpUser, task, between


class AirPulseReadUser(HttpUser):

    wait_time = between(1, 3)

    CITY_IDS = list(range(1, 11))

    @task(4)
    def get_rankings(self):
        with self.client.get(
            "/api/v1/rankings/?limit=10",
            name="/api/v1/rankings",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")
            elif resp.elapsed.total_seconds() > 0.5:
                resp.failure(f"Slow response: {resp.elapsed.total_seconds():.2f}s")

    @task(3)
    def list_cities(self):
        with self.client.get(
            "/api/v1/cities/",
            name="/api/v1/cities",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(2)
    def get_city_air_quality(self):
        city_id = random.choice(self.CITY_IDS)
        with self.client.get(
            f"/api/v1/cities/{city_id}/air-quality?hours=48",
            name="/api/v1/cities/[id]/air-quality",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def get_city_weather(self):
        city_id = random.choice(self.CITY_IDS)
        with self.client.get(
            f"/api/v1/cities/{city_id}/weather?hours=48",
            name="/api/v1/cities/[id]/weather",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def health_check(self):
        self.client.get("/api/v1/admin/health", name="/api/v1/admin/health")
