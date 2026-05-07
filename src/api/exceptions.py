"""
Custom exception classes and exception handlers for the API.
"""
from typing import List

class AppException(Exception):
    """Base application exception"""
    pass

class ResourceNotFoundError(AppException):
    """Resource not found"""
    def __init__(self, resource_type: str, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

class StateTransitionError(AppException):
    """Invalid state transition"""
    def __init__(self, current_state: str, new_state: str, valid_transitions: List):
        self.current_state = current_state
        self.new_state = new_state
        self.valid_transitions = [str(t.value) if hasattr(t, 'value') else str(t) for t in valid_transitions]
        super().__init__(
            f"Invalid transition from {current_state} to {new_state}. "
            f"Valid transitions: {', '.join(self.valid_transitions)}"
        )

class ValidationError(AppException):
    """Validation error"""
    pass

def register_exception_handlers(app):
    """Register FastAPI exception handlers"""
    from fastapi import Request
    from fastapi.responses import JSONResponse

    @app.exception_handler(ResourceNotFoundError)
    async def not_found_handler(request: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": str(exc),
                    "details": {
                        "resource_type": exc.resource_type,
                        "resource_id": exc.resource_id
                    }
                }
            }
        )

    @app.exception_handler(StateTransitionError)
    async def state_transition_handler(request: Request, exc: StateTransitionError):
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "INVALID_STATE_TRANSITION",
                    "message": str(exc),
                    "details": {
                        "current_state": exc.current_state,
                        "requested_state": exc.new_state,
                        "valid_transitions": exc.valid_transitions
                    }
                }
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(exc)
                }
            }
        )
