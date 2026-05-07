"""
Fraud Signal model for storing fraud detection results.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.api.database import Base


class FraudSignal(Base):
    """Fraud signal detected by fraud detection agent"""
    __tablename__ = "fraud_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False, index=True)
    detection_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    overall_risk_score = Column(DECIMAL(3, 2))
    signal_type = Column(String(100))
    severity = Column(DECIMAL(3, 2))
    description = Column(Text)
    evidence = Column(JSON)
    agent_version = Column(String(50))

    # Relationship
    claim = relationship("Claim", back_populates="fraud_signals")

    def __repr__(self):
        return f"<FraudSignal(id={self.id}, claim_id={self.claim_id}, type={self.signal_type}, severity={self.severity})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'claim_id': self.claim_id,
            'detection_timestamp': self.detection_timestamp.isoformat() if self.detection_timestamp else None,
            'overall_risk_score': float(self.overall_risk_score) if self.overall_risk_score else None,
            'signal_type': self.signal_type,
            'severity': float(self.severity) if self.severity else None,
            'description': self.description,
            'evidence': self.evidence,
            'agent_version': self.agent_version
        }
