"""
Customer and CustomerPolicy models.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.api.database import Base

class Customer(Base):
    __tablename__ = "customers"

    # Primary Key
    customer_id = Column(Integer, primary_key=True)

    # Customer Information
    fname = Column(String(50), nullable=False)
    lname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    state = Column(String(2), nullable=True)  # NEW: 2-letter state code

    # Relationships
    policies = relationship("CustomerPolicy", back_populates="customer")
    claims = relationship("Claim", back_populates="customer")
    vehicles = relationship("Vehicle", back_populates="customer")
    agent_logs = relationship("AgentUsageLog", back_populates="customer")

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, name={self.fname} {self.lname})>"


class CustomerPolicy(Base):
    __tablename__ = "customer_policy"

    # Composite Primary Key
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), primary_key=True)
    policy_number = Column(String(50), ForeignKey("policies.policy_number"), primary_key=True)

    # Relationships
    customer = relationship("Customer", back_populates="policies")
    policy = relationship("Policy", back_populates="customers")

    def __repr__(self):
        return f"<CustomerPolicy(customer_id={self.customer_id}, policy={self.policy_number})>"
