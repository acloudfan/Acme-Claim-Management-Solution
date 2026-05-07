"""
Risk Assessment model for storing actuarial risk analysis.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.api.database import Base


class RiskAssessment(Base):
    """Risk assessment result from risk estimation agent"""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False, index=True)
    assessment_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    risk_score = Column(DECIMAL(3, 2))
    cost_deviation_pct = Column(DECIMAL(5, 2))
    risk_factors = Column(JSON)
    recommendation = Column(String(50))
    reasoning = Column(Text)
    confidence = Column(DECIMAL(3, 2))
    agent_version = Column(String(50))

    # Relationship
    claim = relationship("Claim", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, claim_id={self.claim_id}, risk_score={self.risk_score}, recommendation={self.recommendation})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'claim_id': self.claim_id,
            'assessment_timestamp': self.assessment_timestamp.isoformat() if self.assessment_timestamp else None,
            'risk_score': float(self.risk_score) if self.risk_score else None,
            'cost_deviation_pct': float(self.cost_deviation_pct) if self.cost_deviation_pct else None,
            'risk_factors': self.risk_factors,
            'recommendation': self.recommendation,
            'reasoning': self.reasoning,
            'confidence': float(self.confidence) if self.confidence else None,
            'agent_version': self.agent_version
        }
