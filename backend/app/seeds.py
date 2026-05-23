import structlog
from sqlalchemy.orm import Session
from app.models.city import City

log = structlog.get_logger()

CITIES = [
    {
        "name": "Warsaw",
        "country": "Poland",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "iqair_city": "Warsaw",
        "iqair_state": "Masovian Voivodeship",
        "iqair_country": "Poland",
    },
    {
        "name": "Krakow",
        "country": "Poland",
        "latitude": 50.0647,
        "longitude": 19.9450,
        "iqair_city": "Krakow",
        "iqair_state": "Lesser Poland Voivodeship",
        "iqair_country": "Poland",
    },
    {
        "name": "Berlin",
        "country": "Germany",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "iqair_city": "Berlin",
        "iqair_state": "Berlin",
        "iqair_country": "Germany",
    },
    {
        "name": "Prague",
        "country": "Czech Republic",
        "latitude": 50.0755,
        "longitude": 14.4378,
        "iqair_city": "Prague",
        "iqair_state": "Prague",
        "iqair_country": "Czech Republic",
    },
    {
        "name": "Vienna",
        "country": "Austria",
        "latitude": 48.2082,
        "longitude": 16.3738,
        "iqair_city": "Vienna",
        "iqair_state": "Vienna",
        "iqair_country": "Austria",
    },
    {
        "name": "Paris",
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "iqair_city": "Paris",
        "iqair_state": "Ile-de-France",
        "iqair_country": "France",
    },
    {
        "name": "London",
        "country": "United Kingdom",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "iqair_city": "London",
        "iqair_state": "England",
        "iqair_country": "United Kingdom",
    },
    {
        "name": "Madrid",
        "country": "Spain",
        "latitude": 40.4168,
        "longitude": -3.7038,
        "iqair_city": "Madrid",
        "iqair_state": "Community of Madrid",
        "iqair_country": "Spain",
    },
    {
        "name": "Rome",
        "country": "Italy",
        "latitude": 41.9028,
        "longitude": 12.4964,
        "iqair_city": "Rome",
        "iqair_state": "Lazio",
        "iqair_country": "Italy",
    },
    {
        "name": "Amsterdam",
        "country": "Netherlands",
        "latitude": 52.3676,
        "longitude": 4.9041,
        "iqair_city": "Amsterdam",
        "iqair_state": "North Holland",
        "iqair_country": "Netherlands",
    },
]


def seed_cities(db: Session) -> None:
    if db.query(City).count() > 0:
        log.info("seed_skipped", reason="Cities already present in database")
        return

    for data in CITIES:
        db.add(City(**data))

    db.commit()
    log.info("seed_complete", city_count=len(CITIES))
