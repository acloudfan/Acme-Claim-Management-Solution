"""
Agent Usage Log model for tracking LLM API calls.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from src.api.database import Base


class AgentUsageLog(Base):
    """Agent usage log for cost monitoring and analytics"""
    __tablename__ = "agent_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    agent_name = Column(String(100), nullable=False, index=True)
    llm_provider = Column(String(50))
    llm_model = Column(String(100))
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(DECIMAL(10, 6), default=0.0)
    duration_ms = Column(Integer, default=0)
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True, index=True)
    request_type = Column(String(50))
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    claim = relationship("Claim", back_populates="agent_logs")
    customer = relationship("Customer", back_populates="agent_logs")

    def __repr__(self):
        return f"<AgentUsageLog(id={self.id}, agent={self.agent_name}, tokens={self.total_tokens}, cost=${self.estimated_cost_usd})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'agent_name': self.agent_name,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'estimated_cost_usd': float(self.estimated_cost_usd) if self.estimated_cost_usd else 0.0,
            'duration_ms': self.duration_ms,
            'claim_id': self.claim_id,
            'customer_id': self.customer_id,
            'request_type': self.request_type,
            'success': self.success,
            'error_message': self.error_message
        }
