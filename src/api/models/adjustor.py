"""
Adjustor model for insurance claim adjustors.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from src.api.database import Base


class Adjustor(Base):
    __tablename__ = "adjustors"

    # Primary Key
    adjustor_id = Column(String(20), primary_key=True)

    # Adjustor Information
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default='active')  # 'active' or 'inactive'

    # Relationships (optional for P2)
    # assigned_claims = relationship("Claim", back_populates="adjustor")

    def __repr__(self):
        return f"<Adjustor(adjustor_id={self.adjustor_id}, name={self.name})>"
