"""
Customer service for customer CRUD operations.
"""
from sqlalchemy.orm import Session, joinedload
from src.api.models.customer import Customer, CustomerPolicy
from src.api.schemas.customer import CustomerCreate, CustomerUpdate, CustomerPatch
from src.api.services.base_service import BaseService
from src.api.exceptions import ResourceNotFoundError, ValidationError
from typing import Optional

class CustomerService(BaseService):
    """Service for customer operations"""

    def get_customer(self, customer_id: int, include_policies: bool = False) -> Customer:
        """
        Get customer by ID.

        Args:
            customer_id: Customer ID
            include_policies: Include related policies and vehicles

        Returns:
            Customer instance

        Raises:
            ResourceNotFoundError: If customer not found
        """
        query = self.db.query(Customer)

        if include_policies:
            query = query.options(
                joinedload(Customer.policies).joinedload(CustomerPolicy.policy)
            )

        customer = query.filter(Customer.customer_id == customer_id).first()

        if not customer:
            raise ResourceNotFoundError("Customer", customer_id)

        return customer

    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """
        Create new customer.

        Args:
            customer_data: Customer creation data

        Returns:
            Created Customer instance

        Raises:
            ValidationError: If email already exists
        """
        # Check for duplicate email
        if customer_data.email:
            existing = self.db.query(Customer).filter(
                Customer.email == customer_data.email
            ).first()
            if existing:
                raise ValidationError(f"Email {customer_data.email} already exists")

        customer = Customer(
            fname=customer_data.fname,
            lname=customer_data.lname,
            email=customer_data.email,
            phone=customer_data.phone,
            address=customer_data.address
        )

        self.db.add(customer)
        self.commit()
        self.refresh(customer)

        self.logger.info(f"Created customer {customer.customer_id}: {customer.fname} {customer.lname}")
        return customer

    def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Customer:
        """
        Update customer (full update - all fields required).

        Args:
            customer_id: Customer ID
            customer_data: Complete customer data

        Returns:
            Updated Customer instance

        Raises:
            ResourceNotFoundError: If customer not found
            ValidationError: If email already exists for another customer
        """
        customer = self.get_customer(customer_id)

        # Check for duplicate email (excluding current customer)
        if customer_data.email:
            existing = self.db.query(Customer).filter(
                Customer.email == customer_data.email,
                Customer.customer_id != customer_id
            ).first()
            if existing:
                raise ValidationError(f"Email {customer_data.email} already exists")

        # Update all fields
        customer.fname = customer_data.fname
        customer.lname = customer_data.lname
        customer.email = customer_data.email
        customer.phone = customer_data.phone
        customer.address = customer_data.address

        self.commit()
        self.refresh(customer)

        self.logger.info(f"Updated customer {customer_id}")
        return customer

    def patch_customer(self, customer_id: int, customer_data: CustomerPatch) -> Customer:
        """
        Partially update customer.

        Args:
            customer_id: Customer ID
            customer_data: Fields to update (all optional)

        Returns:
            Updated Customer instance

        Raises:
            ResourceNotFoundError: If customer not found
            ValidationError: If email already exists for another customer
        """
        customer = self.get_customer(customer_id)

        # Check for duplicate email if being updated
        if customer_data.email is not None:
            existing = self.db.query(Customer).filter(
                Customer.email == customer_data.email,
                Customer.customer_id != customer_id
            ).first()
            if existing:
                raise ValidationError(f"Email {customer_data.email} already exists")

        # Update only provided fields
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        self.commit()
        self.refresh(customer)

        self.logger.info(f"Patched customer {customer_id}: {list(update_data.keys())}")
        return customer
