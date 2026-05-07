"""
Base agent class for all LLM-powered agents.
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

from .llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """
    Result from agent execution.

    Attributes:
        success: Whether execution was successful
        data: Result data (agent-specific structure)
        error: Error message if failed
        execution_time_ms: Execution duration in milliseconds
        input_tokens: LLM input tokens used
        output_tokens: LLM output tokens used
        agent_name: Name of the agent
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    agent_name: str = ""

    @property
    def total_tokens(self) -> int:
        """Total tokens used"""
        return self.input_tokens + self.output_tokens


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    All agent implementations must extend this class and implement the execute() method.
    """

    def __init__(self, llm_client: BaseLLMClient, config: Dict[str, Any]):
        """
        Initialize base agent.

        Args:
            llm_client: LLM client instance
            config: Agent configuration dictionary
        """
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's task.

        Args:
            input_data: Input data for the agent (agent-specific structure)

        Returns:
            AgentResult with execution results

        Raises:
            Exception: If execution fails
        """
        pass

    def _create_result(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_time_ms: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> AgentResult:
        """
        Helper method to create AgentResult.

        Args:
            success: Whether execution was successful
            data: Result data
            error: Error message
            execution_time_ms: Execution time
            input_tokens: Input tokens used
            output_tokens: Output tokens used

        Returns:
            AgentResult object
        """
        return AgentResult(
            success=success,
            data=data,
            error=error,
            execution_time_ms=execution_time_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            agent_name=self.__class__.__name__
        )

    def _measure_execution_time(self, start_time: datetime) -> int:
        """
        Calculate execution time in milliseconds.

        Args:
            start_time: Execution start datetime

        Returns:
            Duration in milliseconds
        """
        duration = datetime.now() - start_time
        return int(duration.total_seconds() * 1000)
