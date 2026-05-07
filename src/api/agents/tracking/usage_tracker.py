"""
Usage tracker for monitoring LLM API calls and costs.
"""
import logging
import functools
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.api.models.agent_usage_log import AgentUsageLog
from src.api.agents.base_agent import AgentResult

logger = logging.getLogger(__name__)


# Cost estimates per 1M tokens (USD)
COST_ESTIMATES = {
    'anthropic_claude_sonnet_input': 3.00,
    'anthropic_claude_sonnet_output': 15.00,
    'anthropic_claude_opus_input': 15.00,
    'anthropic_claude_opus_output': 75.00,
    'openai_gpt4_turbo_input': 10.00,
    'openai_gpt4_turbo_output': 30.00,
    'bedrock_claude_3_sonnet_input': 3.00,
    'bedrock_claude_3_sonnet_output': 15.00,
    'bedrock_claude_3_opus_input': 15.00,
    'bedrock_claude_3_opus_output': 75.00,
    'bedrock_claude_3_haiku_input': 0.25,
    'bedrock_claude_3_haiku_output': 1.25,
}


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate estimated cost for LLM API call.

    Args:
        provider: LLM provider ('anthropic', 'openai', 'bedrock')
        model: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD
    """
    try:
        # Determine cost key based on provider and model
        if provider == 'anthropic':
            if 'opus' in model.lower():
                input_cost_key = 'anthropic_claude_opus_input'
                output_cost_key = 'anthropic_claude_opus_output'
            else:  # Sonnet or default
                input_cost_key = 'anthropic_claude_sonnet_input'
                output_cost_key = 'anthropic_claude_sonnet_output'

        elif provider == 'openai':
            input_cost_key = 'openai_gpt4_turbo_input'
            output_cost_key = 'openai_gpt4_turbo_output'

        elif provider == 'bedrock':
            if 'opus' in model.lower():
                input_cost_key = 'bedrock_claude_3_opus_input'
                output_cost_key = 'bedrock_claude_3_opus_output'
            elif 'haiku' in model.lower():
                input_cost_key = 'bedrock_claude_3_haiku_input'
                output_cost_key = 'bedrock_claude_3_haiku_output'
            else:  # Sonnet or default
                input_cost_key = 'bedrock_claude_3_sonnet_input'
                output_cost_key = 'bedrock_claude_3_sonnet_output'

        else:
            logger.warning(f"Unknown provider '{provider}', using default cost")
            input_cost_key = 'anthropic_claude_sonnet_input'
            output_cost_key = 'anthropic_claude_sonnet_output'

        # Calculate cost
        input_cost_per_1m = COST_ESTIMATES.get(input_cost_key, 3.00)
        output_cost_per_1m = COST_ESTIMATES.get(output_cost_key, 15.00)

        input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_1m

        return input_cost + output_cost

    except Exception as e:
        logger.error(f"Error calculating cost: {e}")
        return 0.0


def log_usage(
    db: Session,
    agent_name: str,
    llm_provider: str,
    llm_model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    claim_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    request_type: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> None:
    """
    Log LLM usage to database.

    Args:
        db: Database session
        agent_name: Name of the agent
        llm_provider: LLM provider
        llm_model: Model identifier
        input_tokens: Input tokens used
        output_tokens: Output tokens used
        duration_ms: Execution duration in milliseconds
        claim_id: Claim ID if applicable
        customer_id: Customer ID if applicable
        request_type: Type of request
        success: Whether request was successful
        error_message: Error message if failed
    """
    try:
        total_tokens = input_tokens + output_tokens
        estimated_cost = calculate_cost(llm_provider, llm_model, input_tokens, output_tokens)

        usage_log = AgentUsageLog(
            agent_name=agent_name,
            llm_provider=llm_provider,
            llm_model=llm_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
            duration_ms=duration_ms,
            claim_id=claim_id,
            customer_id=customer_id,
            request_type=request_type,
            success=success,
            error_message=error_message
        )

        db.add(usage_log)
        db.commit()

        logger.info(
            f"Logged usage: {agent_name} | {total_tokens} tokens | "
            f"${estimated_cost:.6f} | {duration_ms}ms"
        )

    except Exception as e:
        logger.error(f"Failed to log usage: {e}")
        db.rollback()


def track_usage(
    db: Session,
    claim_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    request_type: Optional[str] = None
) -> Callable:
    """
    Decorator to track agent usage automatically.

    Usage:
        @track_usage(db=db, claim_id=123, request_type="fraud_detection")
        async def my_agent_function():
            # Agent logic here
            return agent_result

    Args:
        db: Database session
        claim_id: Claim ID if applicable
        customer_id: Customer ID if applicable
        request_type: Type of request

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> AgentResult:
            start_time = datetime.now()
            result = None
            error = None

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                error = str(e)
                raise

            finally:
                # Calculate duration
                duration = datetime.now() - start_time
                duration_ms = int(duration.total_seconds() * 1000)

                # Extract usage info from result if available
                if result and isinstance(result, AgentResult):
                    log_usage(
                        db=db,
                        agent_name=result.agent_name,
                        llm_provider=kwargs.get('llm_provider', 'unknown'),
                        llm_model=kwargs.get('llm_model', 'unknown'),
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        duration_ms=duration_ms,
                        claim_id=claim_id,
                        customer_id=customer_id,
                        request_type=request_type,
                        success=result.success,
                        error_message=result.error
                    )
                elif error:
                    log_usage(
                        db=db,
                        agent_name=func.__name__,
                        llm_provider=kwargs.get('llm_provider', 'unknown'),
                        llm_model=kwargs.get('llm_model', 'unknown'),
                        input_tokens=0,
                        output_tokens=0,
                        duration_ms=duration_ms,
                        claim_id=claim_id,
                        customer_id=customer_id,
                        request_type=request_type,
                        success=False,
                        error_message=error
                    )

        return wrapper
    return decorator
