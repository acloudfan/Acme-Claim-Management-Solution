"""
Vehicle model.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.api.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    # Primary Key
    vin = Column(String(17), primary_key=True)

    # Foreign Key
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)

    # Vehicle Information
    year = Column(Integer, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    color = Column(String(30), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="vehicles")
    claims = relationship("Claim", back_populates="vehicle")
    policies = relationship("PolicyVehicle", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle(vin={self.vin}, {self.year} {self.make} {self.model})>"
