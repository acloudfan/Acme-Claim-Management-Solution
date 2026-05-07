"""
Database models for the Insurance Claims API.
"""
from src.api.models.customer import Customer, CustomerPolicy
from src.api.models.vehicle import Vehicle
from src.api.models.policy import Policy, PolicyVehicle
from src.api.models.claim import Claim, ClaimImage
from src.api.models.damage import Damage
from src.api.models.claim_event import ClaimEvent
from src.api.models.adjustor import Adjustor
from src.api.models.agent_usage_log import AgentUsageLog
from src.api.models.fraud_signal import FraudSignal
from src.api.models.risk_assessment import RiskAssessment

__all__ = [
    "Customer",
    "CustomerPolicy",
    "Vehicle",
    "Policy",
    "PolicyVehicle",
    "Claim",
    "ClaimImage",
    "Damage",
    "ClaimEvent",
    "Adjustor",
    "AgentUsageLog",
    "FraudSignal",
    "RiskAssessment"
]
