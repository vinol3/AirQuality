"""City model — the central entity all readings are linked to."""
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.models.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # IQAir API requires city + state + country for lookups
    iqair_city = Column(String(100))
    iqair_state = Column(String(100))
    iqair_country = Column(String(100))

    # Relationships — used when loading city with its readings
    air_quality_readings = relationship(
        "AirQualityReading", back_populates="city", lazy="dynamic"
    )
    weather_readings = relationship(
        "WeatherReading", back_populates="city", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<City id={self.id} name={self.name}>"
