"""
Common schemas for pagination, errors, and success responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List

# Generic type for data responses
T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str
    message: str
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: ErrorDetail

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool
