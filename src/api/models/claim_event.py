"""
ClaimEvent model for audit trail and event logging.
"""
from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from src.api.database import Base
from datetime import date, datetime

class ClaimEvent(Base):
    __tablename__ = "claims_events"

    # Primary Key
    event_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False)

    # Event Information
    event_date = Column(Date, nullable=False, default=date.today)
    event_time = Column(Time, nullable=False, default=lambda: datetime.now().time())
    status = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    action_by = Column(String(50), nullable=False)  # Actor type
    action_by_identity = Column(String(100), nullable=False)  # Actor identifier
    comments = Column(String(500), nullable=True)

    # Relationships
    claim = relationship("Claim", back_populates="events")

    def __repr__(self):
        return f"<ClaimEvent(event_id={self.event_id}, claim_id={self.claim_id}, action={self.action})>"
