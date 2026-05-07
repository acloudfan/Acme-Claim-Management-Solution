"""
Policy and PolicyVehicle models.
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from src.api.database import Base

class Policy(Base):
    __tablename__ = "policies"

    # Primary Key
    policy_number = Column(String(50), primary_key=True)

    # Foreign Key
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)

    # Policy Information
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    policyholder_name = Column(String(100), nullable=False)
    insured_name = Column(String(100), nullable=False)
    additional_insured_1 = Column(String(100), nullable=True)
    additional_insured_2 = Column(String(100), nullable=True)
    additional_insured_3 = Column(String(100), nullable=True)

    # Coverage Limits
    bodily_injury_limit = Column(Numeric(10, 2), nullable=False)
    property_damage_limit = Column(Numeric(10, 2), nullable=False)
    deductible = Column(Numeric(10, 2), nullable=False)
    premium = Column(Numeric(10, 2), nullable=False)

    # Relationships
    customers = relationship("CustomerPolicy", back_populates="policy")
    vehicles = relationship("PolicyVehicle", back_populates="policy")
    claims = relationship("Claim", back_populates="policy")

    def __repr__(self):
        return f"<Policy(policy_number={self.policy_number}, holder={self.policyholder_name})>"


class PolicyVehicle(Base):
    __tablename__ = "policy_vehicle"

    # Composite Primary Key
    policy_number = Column(String(50), ForeignKey("policies.policy_number"), primary_key=True)
    vin = Column(String(17), ForeignKey("vehicles.vin"), primary_key=True)

    # Relationships
    policy = relationship("Policy", back_populates="vehicles")
    vehicle = relationship("Vehicle", back_populates="policies")

    def __repr__(self):
        return f"<PolicyVehicle(policy={self.policy_number}, vin={self.vin})>"
