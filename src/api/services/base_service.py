"""
Base service class for all business logic services.
"""
from sqlalchemy.orm import Session
import logging

class BaseService:
    """Base class for all services"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def commit(self):
        """Commit database transaction"""
        try:
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Commit failed: {e}")
            self.db.rollback()
            raise

    def refresh(self, instance):
        """Refresh instance from database"""
        self.db.refresh(instance)
