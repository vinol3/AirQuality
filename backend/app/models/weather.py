from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)

    temperature = Column(Float)   
    humidity = Column(Integer)     
    wind_speed = Column(Float)    
    pressure = Column(Integer)     
    description = Column(String(100))  

    source = Column(String(50), default="openweathermap")

    city = relationship("City", back_populates="weather_readings")

    def __repr__(self) -> str:
        return f"<WeatherReading city_id={self.city_id} temp={self.temperature}°C at={self.recorded_at}>"
