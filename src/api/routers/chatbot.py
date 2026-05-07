"""
Chatbot API router for customer-facing chat interface.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from ..agents.chatbot.chatbot_agent import ChatbotAgent
from ..agents.chatbot.session_manager import get_session_manager
from ..agents.llm.factory import get_llm_client
from ..agents.llm.config import load_llm_config
from ..config import get_settings
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])


class ChatMessageRequest(BaseModel):
    """Request schema for sending chat message"""
    customer_id: int = Field(..., description="Customer ID")
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID (auto-created if not provided)")
    context: Optional[Dict[str, Any]] = Field(None, description="Page context from frontend")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 100,
                "message": "What's the status of my claim?",
                "session_id": "abc-123-def",
                "context": {
                    "page": "claim_detail",
                    "claim_id": 123,
                    "claim_data": {
                        "status": "approved",
                        "total_cost": 2500.00
                    }
                }
            }
        }


class ChatMessageResponse(BaseModel):
    """Response schema for chat message"""
    session_id: str = Field(..., description="Session ID for conversation continuity")
    response: str = Field(..., description="Assistant's response")
    tool_calls: Optional[List[Dict[str, str]]] = Field(None, description="Tools called during processing")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123-def",
                "response": "Your claim #123 is currently approved. The estimated repair cost is $2,500.",
                "tool_calls": [
                    {
                        "tool": "get_claim_status",
                        "result": "Claim #123 status: approved"
                    }
                ]
            }
        }


@router.post("/customer/message", response_model=ChatMessageResponse)
async def send_customer_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to the customer chatbot.

    The chatbot can:
    - Answer questions about claims, policies, and processes
    - Look up real-time claim status
    - Search FAQ knowledge base
    - Explain cost estimates

    Context-aware: Pass page context to get contextual answers without tool calls.
    """
    try:
        session_manager = get_session_manager()
        settings = get_settings()

        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.create_session(request.customer_id)
            logger.info(f"Created new session {session_id} for customer {request.customer_id}")
        else:
            # Verify session exists and belongs to customer
            session = session_manager.get_session(session_id)
            if not session:
                # Session expired or invalid, create new one
                session_id = session_manager.create_session(request.customer_id)
                logger.info(f"Session expired, created new session {session_id}")
            elif session['customer_id'] != request.customer_id:
                raise HTTPException(
                    status_code=403,
                    detail="Session does not belong to this customer"
                )

        # Get conversation history
        history = session_manager.get_history(session_id)

        # Initialize chatbot agent
        llm_config = load_llm_config(
            settings.config.get('llm', {}).get('default_provider', 'anthropic'),
            settings.config
        )
        llm_client = get_llm_client(llm_config)
        chatbot = ChatbotAgent(llm_client, settings.config, db)

        # Execute chatbot with optional context
        result = await chatbot.execute({
            'customer_id': request.customer_id,
            'message': request.message,
            'conversation_history': history,
            'context': request.context  # Pass page context to agent
        })

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Chatbot processing failed: {result.error}"
            )

        # Update session history
        session_manager.update_session(
            session_id,
            request.message,
            result.data['response']
        )

        logger.info(
            f"Chatbot response for customer {request.customer_id}: "
            f"{result.execution_time_ms}ms, {result.total_tokens} tokens"
        )

        return ChatMessageResponse(
            session_id=session_id,
            response=result.data['response'],
            tool_calls=result.data.get('tool_calls')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your message"
        )


@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session.

    Use this to clear conversation history or logout.
    """
    session_manager = get_session_manager()
    deleted = session_manager.delete_session(session_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True, "message": "Session deleted"}


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.

    Returns list of messages with role (user/assistant) and content.
    """
    session_manager = get_session_manager()
    history = session_manager.get_history(session_id)

    if history is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return {
        "session_id": session_id,
        "message_count": len(history),
        "history": [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]
    }


@router.get("/stats")
async def get_chatbot_stats():
    """
    Get chatbot statistics (admin endpoint).

    Returns active session count and other metrics.
    """
    session_manager = get_session_manager()

    return {
        "active_sessions": session_manager.get_active_session_count(),
        "status": "operational"
    }


# Placeholder endpoints for future chatbot types
@router.post("/adjustor/message")
async def send_adjustor_message():
    """
    Adjustor chatbot (not implemented yet).

    Future: AI assistant for claims adjustors with access to
    fraud detection insights, claim analytics, and damage history.
    """
    raise HTTPException(
        status_code=501,
        detail="Adjustor chatbot not implemented yet (planned for future release)"
    )


@router.post("/executive/message")
async def send_executive_message():
    """
    Executive chatbot (not implemented yet).

    Future: AI assistant for executives with business KPIs,
    trend analysis, and cost reports.
    """
    raise HTTPException(
        status_code=501,
        detail="Executive chatbot not implemented yet (planned for future release)"
    )
