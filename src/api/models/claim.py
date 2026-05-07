"""
Claim and ClaimImage models.
"""
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.api.database import Base
from datetime import date, time, datetime

class Claim(Base):
    __tablename__ = "claims"

    # Primary Key
    claim_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    vin = Column(String(17), ForeignKey("vehicles.vin"), nullable=False)
    policy_number = Column(String(50), ForeignKey("policies.policy_number"), nullable=False)

    # FNOL Information
    fnol_date = Column(Date, nullable=False, default=date.today)
    fnol_time = Column(Time, nullable=False, default=lambda: datetime.now().time())
    date_of_damage = Column(Date, nullable=False)
    is_drivable = Column(Boolean, nullable=False)
    incident_description = Column(Text, nullable=True)  # Customer's description of what happened

    # Status Tracking
    current_status = Column(String(50), nullable=False, default="draft")
    claim_closed = Column(Boolean, default=False)
    claim_closed_date = Column(Date, nullable=True)

    # AI/Human Review Flags
    ai_estimate_accepted = Column(Boolean, default=False)
    routed_to_traditional = Column(Boolean, default=False)
    reason_routing_to_traditional = Column(String(255), nullable=True)

    # Appeal Tracking
    appeal_count = Column(Integer, default=0)  # Number of appeals (0, 1, or 2)
    first_appeal_reason = Column(Text, nullable=True)  # Customer's reason for first appeal
    first_appeal_date = Column(Date, nullable=True)  # Date of first appeal
    second_appeal_reason = Column(Text, nullable=True)  # Customer's reason for second appeal
    second_appeal_date = Column(Date, nullable=True)  # Date of second appeal

    # Adjustor Assignment
    assigned_adjustor_id = Column(String(20), ForeignKey("adjustors.adjustor_id"), nullable=True)

    # Estimate Reference
    active_estimate_id = Column(String(100), nullable=True)

    # Financial Information
    claim_amount = Column(Numeric(10, 2), nullable=True)
    actual_claim_amount = Column(Numeric(10, 2), nullable=True)

    # Labor Rate Fields (NEW)
    state_avg_labor_cost = Column(Numeric(10, 2), nullable=True)  # $/hour
    labor_rate_state = Column(String(2), nullable=True)  # State code
    labor_rate_source = Column(String(20), default="customer_state")  # Source

    # Agent-Enhanced Fields (nullable for backward compatibility)
    overall_fraud_risk_score = Column(Numeric(3, 2), nullable=True)  # Aggregate fraud risk score
    overall_risk_score = Column(Numeric(3, 2), nullable=True)  # Aggregate actuarial risk score
    agent_flags = Column(Text, nullable=True)  # JSON string of agent flags/warnings

    # Relationships
    customer = relationship("Customer", back_populates="claims")
    vehicle = relationship("Vehicle", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    images = relationship("ClaimImage", back_populates="claim", cascade="all, delete-orphan")
    damages = relationship("Damage", back_populates="claim", cascade="all, delete-orphan")
    events = relationship("ClaimEvent", back_populates="claim", cascade="all, delete-orphan")
    agent_logs = relationship("AgentUsageLog", back_populates="claim")
    fraud_signals = relationship("FraudSignal", back_populates="claim")
    risk_assessments = relationship("RiskAssessment", back_populates="claim")

    def __repr__(self):
        return f"<Claim(claim_id={self.claim_id}, status={self.current_status})>"


class ClaimImage(Base):
    __tablename__ = "claim_images"

    # Composite Primary Key (claim_id, image_id)
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), primary_key=True, nullable=False)
    image_id = Column(String(255), primary_key=True)

    # Metadata
    uploaded_at = Column(DateTime, nullable=False, default=datetime.now)
    uploaded_by = Column(String(100), nullable=False)

    # Relationships
    claim = relationship("Claim", back_populates="images")
    damages = relationship("Damage", back_populates="image", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClaimImage(image_id={self.image_id}, claim_id={self.claim_id})>"
