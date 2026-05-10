"""
Damage model for damage assessments and estimates.
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text, Date, Time, Boolean, DateTime
from sqlalchemy.orm import relationship
from src.api.database import Base

class Damage(Base):
    __tablename__ = "damages"

    # Primary Key
    damage_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False)
    estimate_id = Column(String(100), nullable=False)
    image_id = Column(String(255), ForeignKey("claim_images.image_id"), nullable=False)

    # Estimate Type
    estimate_type = Column(String(20), nullable=False)  # 'ai' or 'human'

    # YOLO Detection Fields
    damage_class = Column(Integer, nullable=True)  # YOLO class ID (0-13)
    damage_confidence = Column(Numeric(5, 2), nullable=True)  # YOLO confidence (0.0-1.0)
    damage_part = Column(String(100), nullable=False)

    # Bounding Box Coordinates
    bounding_box_x = Column(Integer, nullable=True)
    bounding_box_y = Column(Integer, nullable=True)
    bounding_box_width = Column(Integer, nullable=True)
    bounding_box_height = Column(Integer, nullable=True)

    # LLM Assessment Fields (populated by Damage Assessment Agent if enabled, otherwise YOLO heuristics)
    internal_damage_probability = Column(Numeric(5, 2), nullable=True)  # LLM: Probability of internal damage (0.0-1.0)
    severity = Column(Numeric(5, 2), nullable=False)  # LLM: Damage severity score (0.0-1.0)
    recommended_action = Column(String(50), nullable=True)  # LLM: repaint|de-dent|replace|de-dent-and-paint
    reasoning = Column(Text, nullable=True)  # LLM: Detailed assessment reasoning
    car_side = Column(String(20), nullable=True)  # LLM: front|back|driver_side|passenger_side
    assessment_confidence = Column(Numeric(5, 2), nullable=True)  # LLM: Assessment confidence (0.0-1.0)

    # Agent-Enhanced Fields (nullable for backward compatibility)
    enhanced_severity = Column(Numeric(3, 2), nullable=True)  # Agent-refined severity score
    ai_generated_probability = Column(Numeric(3, 2), nullable=True)  # Probability image is AI-generated
    fraud_risk_score = Column(Numeric(3, 2), nullable=True)  # Fraud risk for this specific damage
    risk_score = Column(Numeric(3, 2), nullable=True)  # Actuarial risk score
    agent_reasoning = Column(Text, nullable=True)  # Agent's reasoning for assessments
    secondary_damages_predicted = Column(Text, nullable=True)  # JSON string of predicted secondary damages
    damage_summary = Column(Text, nullable=True)  # Damage assessment summary from LLM agent

    # Annotated Image Reference
    annotated_image_id = Column(String(255), nullable=True)  # Filename with BB- prefix

    # ============================================================================
    # DUAL-COLUMN APPROACH: AI vs Adjustor Estimates
    # ============================================================================
    # AI Estimates (IMMUTABLE - Set once during AI estimation)
    ai_labor_hours = Column(Numeric(5, 2), nullable=False)
    ai_parts_cost = Column(Numeric(10, 2), nullable=False)
    ai_total_cost = Column(Numeric(10, 2), nullable=False)

    # Adjustor Estimates (NULLABLE - Set during human review)
    adjustor_labor_hours = Column(Numeric(5, 2), nullable=True)
    adjustor_parts_cost = Column(Numeric(10, 2), nullable=True)
    adjustor_total_cost = Column(Numeric(10, 2), nullable=True)
    adjustor_note = Column(Text, nullable=True)
    reviewed_by_adjustor = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)
    # ============================================================================

    # Timestamp Fields (when estimate was generated)
    generated_on_date = Column(Date, nullable=True)
    generated_on_time = Column(Time, nullable=True)

    # DEPRECATED: Use claim.state_avg_labor_cost
    avg_labor_cost = Column(Numeric(10, 2), nullable=True)

    # Relationships
    claim = relationship("Claim", back_populates="damages")
    image = relationship("ClaimImage", back_populates="damages")

    def __repr__(self):
        return f"<Damage(damage_id={self.damage_id}, part={self.damage_part})>"
