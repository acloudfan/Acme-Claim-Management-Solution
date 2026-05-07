"""
Policy service for policy operations (read-only).
"""
from sqlalchemy.orm import Session
from src.api.models.policy import Policy, PolicyVehicle
from src.api.models.customer import Customer
from src.api.models.vehicle import Vehicle
from src.api.services.base_service import BaseService
from src.api.exceptions import ResourceNotFoundError
from typing import List, Dict, Any


class PolicyService(BaseService):
    """Service for policy operations (read-only)"""

    def get_customer_policies(self, customer_id: int) -> List[Dict[str, Any]]:
        """
        Get all policies for a customer with associated vehicles.

        Args:
            customer_id: Customer ID

        Returns:
            List of policy dictionaries with vehicles

        Raises:
            ResourceNotFoundError: If customer doesn't exist
        """
        # Verify customer exists
        customer = self.db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()

        if not customer:
            raise ResourceNotFoundError("Customer", customer_id)

        # Get policies
        policies = (
            self.db.query(Policy)
            .filter(Policy.customer_id == customer_id)
            .all()
        )

        # Build response data with vehicles
        result = []
        for policy in policies:
            # Get vehicles for this policy
            policy_vehicles = (
                self.db.query(Vehicle)
                .join(PolicyVehicle)
                .filter(PolicyVehicle.policy_number == policy.policy_number)
                .all()
            )

            # Build policy dict manually
            policy_dict = {
                'policy_number': policy.policy_number,
                'customer_id': policy.customer_id,
                'policyholder_name': policy.policyholder_name,
                'insured_name': policy.insured_name,
                'start_date': policy.start_date,
                'end_date': policy.end_date,
                'additional_insured_1': policy.additional_insured_1,
                'additional_insured_2': policy.additional_insured_2,
                'additional_insured_3': policy.additional_insured_3,
                'bodily_injury_limit': policy.bodily_injury_limit,
                'property_damage_limit': policy.property_damage_limit,
                'premium': policy.premium,
                'deductible': policy.deductible,
                'vehicles': [
                    {
                        'vin': v.vin,
                        'year': v.year,
                        'make': v.make,
                        'model': v.model,
                        'color': v.color
                    }
                    for v in policy_vehicles
                ]
            }
            result.append(policy_dict)

        self.logger.info(f"Retrieved {len(result)} policies for customer {customer_id}")
        return result

    def get_policy(self, customer_id: int, policy_number: str) -> Dict[str, Any]:
        """
        Get single policy with vehicles.

        Args:
            customer_id: Customer ID
            policy_number: Policy number

        Returns:
            Policy dictionary with vehicles

        Raises:
            ResourceNotFoundError: If policy doesn't exist or doesn't belong to customer
        """
        policy = (
            self.db.query(Policy)
            .filter(
                Policy.policy_number == policy_number,
                Policy.customer_id == customer_id
            )
            .first()
        )

        if not policy:
            raise ResourceNotFoundError(
                "Policy",
                policy_number,
                f"Policy not found for customer {customer_id}"
            )

        # Load vehicles
        policy_vehicles = (
            self.db.query(Vehicle)
            .join(PolicyVehicle)
            .filter(PolicyVehicle.policy_number == policy.policy_number)
            .all()
        )

        # Build policy dict manually
        policy_dict = {
            'policy_number': policy.policy_number,
            'customer_id': policy.customer_id,
            'policyholder_name': policy.policyholder_name,
            'insured_name': policy.insured_name,
            'start_date': policy.start_date,
            'end_date': policy.end_date,
            'additional_insured_1': policy.additional_insured_1,
            'additional_insured_2': policy.additional_insured_2,
            'additional_insured_3': policy.additional_insured_3,
            'bodily_injury_limit': policy.bodily_injury_limit,
            'property_damage_limit': policy.property_damage_limit,
            'premium': policy.premium,
            'deductible': policy.deductible,
            'vehicles': [
                {
                    'vin': v.vin,
                    'year': v.year,
                    'make': v.make,
                    'model': v.model,
                    'color': v.color
                }
                for v in policy_vehicles
            ]
        }

        self.logger.info(f"Retrieved policy {policy_number} with {len(policy_vehicles)} vehicles")
        return policy_dict
