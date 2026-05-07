"""
Damage service for managing damage records and cost calculations.
"""
from src.api.services.base_service import BaseService
from src.api.models.damage import Damage
from src.api.models.claim import Claim
from sqlalchemy import func
from datetime import date, datetime
from typing import Dict


class DamageService(BaseService):
    """Service for damage-related operations"""

    def create_manual_damage(
        self,
        claim_id: int,
        damage_data: Dict
    ) -> Damage:
        """
        Create a manual damage entry added by an adjustor.

        Args:
            claim_id: Claim identifier
            damage_data: Dictionary with damage details

        Returns:
            Created Damage object
        """
        # Verify claim exists
        claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        # Generate estimate_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        estimate_id = f"{claim_id}_human_{timestamp}"

        # Calculate total cost
        labor_cost = damage_data['labor_hours'] * damage_data['labor_rate']
        total_cost = labor_cost + damage_data['parts_cost']

        # Map severity to decimal
        severity_decimal = self._severity_to_decimal(damage_data['severity'])

        # Create damage record
        damage = Damage(
            claim_id=claim_id,
            estimate_id=estimate_id,
            estimate_type='human',
            image_id=damage_data.get('image_id', 'MANUAL_ENTRY'),
            damage_part=damage_data['damage_part'],
            severity=severity_decimal,
            reasoning=damage_data.get('description', ''),
            estimated_total_cost=total_cost,
            labor_hours=damage_data['labor_hours'],
            avg_labor_cost=damage_data['labor_rate'],
            estimated_parts_cost=damage_data['parts_cost'],
            adjustor_note=damage_data['adjustor_note'],
            generated_on_date=date.today(),
            generated_on_time=datetime.now().time()
        )

        self.db.add(damage)
        self.commit()
        self.refresh(damage)

        # Recalculate claim total
        self.recalculate_claim_total(claim_id)

        self.logger.info(f"Created manual damage {damage.damage_id} for claim {claim_id}")
        return damage

    def update_damage_costs(
        self,
        damage_id: int,
        update_data: Dict
    ) -> Damage:
        """
        Update cost information for an existing damage.

        Args:
            damage_id: Damage identifier
            update_data: Dictionary with fields to update

        Returns:
            Updated Damage object
        """
        damage = self.db.query(Damage).filter(
            Damage.damage_id == damage_id
        ).first()

        if not damage:
            raise ValueError(f"Damage {damage_id} not found")

        # Update provided fields
        updated = False
        if 'labor_hours' in update_data and update_data['labor_hours'] is not None:
            damage.labor_hours = update_data['labor_hours']
            updated = True

        if 'labor_rate' in update_data and update_data['labor_rate'] is not None:
            damage.avg_labor_cost = update_data['labor_rate']
            updated = True

        if 'parts_cost' in update_data and update_data['parts_cost'] is not None:
            damage.estimated_parts_cost = update_data['parts_cost']
            updated = True

        # Recalculate total if any field changed
        if updated:
            damage.estimated_total_cost = (
                damage.labor_hours * damage.avg_labor_cost
            ) + damage.estimated_parts_cost

        # Append adjustor note with timestamp
        if update_data.get('adjustor_note'):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing_note = damage.adjustor_note or ""
            if existing_note:
                damage.adjustor_note = f"{existing_note}\n\n[{timestamp}] {update_data['adjustor_note']}"
            else:
                damage.adjustor_note = f"[{timestamp}] {update_data['adjustor_note']}"

        self.commit()
        self.refresh(damage)

        # Recalculate claim total
        self.recalculate_claim_total(damage.claim_id)

        self.logger.info(f"Updated damage {damage_id} costs")
        return damage

    def recalculate_claim_total(self, claim_id: int) -> float:
        """
        Recalculate total claim amount by summing all damage costs.

        Args:
            claim_id: Claim identifier

        Returns:
            New total amount
        """
        total = self.db.query(
            func.sum(Damage.estimated_total_cost)
        ).filter(
            Damage.claim_id == claim_id
        ).scalar() or 0

        claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
        if claim:
            claim.claim_amount = float(total)
            self.commit()

        self.logger.info(f"Recalculated claim {claim_id} total: ${total:.2f}")
        return float(total)

    def get_damages_by_claim(self, claim_id: int):
        """
        Get all damages for a claim.

        Args:
            claim_id: Claim identifier

        Returns:
            List of Damage objects
        """
        damages = self.db.query(Damage).filter(
            Damage.claim_id == claim_id
        ).all()
        return damages

    def _severity_to_decimal(self, severity: str) -> float:
        """
        Convert severity string to decimal value.

        Args:
            severity: 'light', 'moderate', or 'severe'

        Returns:
            Decimal severity (0.0-1.0)
        """
        mapping = {
            "light": 0.3,
            "moderate": 0.6,
            "severe": 0.9
        }
        return mapping.get(severity.lower(), 0.5)
