from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class AirQualityReading(Base):
    __tablename__ = "air_quality_readings"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)

    aqi = Column(Integer)
    pm25 = Column(Float)          
    pm10 = Column(Float)           

    source = Column(String(50), default="iqair")

    city = relationship("City", back_populates="air_quality_readings")

    def __repr__(self) -> str:
        return f"<AirQualityReading city_id={self.city_id} aqi={self.aqi} at={self.recorded_at}>"
