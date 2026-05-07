"""
Customer-facing chatbot agent with tool calling and context awareness.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message
from .tools import get_chatbot_tools, execute_tool
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ChatbotAgent(BaseAgent):
    """
    Customer-facing chatbot agent.

    Features:
    - Tool calling for database lookups (claims, policies, damages)
    - FAQ search capability
    - Context awareness (receives page context from frontend)
    - Conversation history management
    """

    def __init__(self, llm_client: BaseLLMClient, config: Dict[str, Any], db: Session):
        """
        Initialize chatbot agent.

        Args:
            llm_client: LLM client instance
            config: Agent configuration
            db: Database session for tool calls
        """
        super().__init__(llm_client, config)
        self.tools = get_chatbot_tools()
        self.db = db

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute chatbot conversation turn.

        Args:
            input_data: Dict with:
                - customer_id: int - Customer ID
                - message: str - User's message
                - conversation_history: List[Message] - Previous messages
                - context: dict (optional) - Page context from frontend

        Returns:
            AgentResult with response text and tool calls made
        """
        start_time = datetime.now()

        try:
            customer_id = input_data['customer_id']
            user_message = input_data['message']
            history = input_data.get('conversation_history', [])
            context = input_data.get('context')  # NEW: Optional context from frontend

            logger.info(f"Chatbot processing message for customer {customer_id}")

            # Build conversation messages with context
            messages = history.copy()

            # If context provided, inject it before the user message
            if context:
                context_message = self._build_context_message(context)
                messages.append(Message(role='user', content=context_message))

            messages.append(Message(role='user', content=user_message))

            # System prompt
            system_prompt = self._build_system_prompt(customer_id)

            # Call LLM with tools
            response = self.llm_client.chat_with_tools(
                system=system_prompt,
                messages=messages,
                tools=self.tools,
                temperature=0.3,
                max_tokens=1024
            )

            # Handle tool calls if present
            tool_results = []
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    logger.info(f"Chatbot calling tool: {tool_call.name}")
                    result = await execute_tool(
                        tool_call.name,
                        tool_call.arguments,
                        customer_id,
                        self.db
                    )
                    tool_results.append({
                        'tool': tool_call.name,
                        'result': result
                    })

                # Make follow-up call with tool results
                messages.append(Message(role='assistant', content=response.content or ''))

                tool_result_content = "\n\n".join([
                    f"Tool: {tr['tool']}\nResult: {tr['result']}"
                    for tr in tool_results
                ])

                messages.append(Message(
                    role='user',
                    content=f"[TOOL RESULTS]\n{tool_result_content}\n\nPlease provide a helpful response to the user based on these results."
                ))

                final_response = self.llm_client.chat(
                    system=system_prompt,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024
                )

                response_text = final_response.content
                total_input_tokens = response.input_tokens + final_response.input_tokens
                total_output_tokens = response.output_tokens + final_response.output_tokens
            else:
                response_text = response.content
                total_input_tokens = response.input_tokens
                total_output_tokens = response.output_tokens

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'response': response_text,
                'tool_calls': tool_results if tool_results else None
            }

            logger.info(f"Chatbot completed in {execution_time_ms}ms with {len(tool_results)} tool calls")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        except Exception as e:
            logger.error(f"Chatbot failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={'response': "I'm sorry, I'm having trouble processing your request right now. Please try again or contact support."},
                error=str(e)
            )

    def _build_system_prompt(self, customer_id: int) -> str:
        """Build system prompt for chatbot"""
        return f"""You are a helpful insurance claims assistant for customer {customer_id}.

Your role is to:
- Answer questions about claims, policies, and insurance processes
- Look up real-time claim status and details using available tools
- Explain cost estimates in simple language
- Guide customers through the claims process
- Provide friendly, professional customer service

Guidelines:
- Be conversational and empathetic
- Use simple language, avoid jargon
- If you need specific information, use the available tools
- If you don't know something, admit it and offer to connect them with a human agent
- Always prioritize accuracy over speed
- When context about the current page is provided, use it to give contextual answers

When a customer asks about their claim or policy, use the appropriate tool to retrieve current information."""

    def _build_context_message(self, context: dict) -> str:
        """
        Build a context message from frontend-provided page context.

        Context can include:
        - page: Current page name (e.g., "claim_detail", "dashboard")
        - claim_id: ID of claim being viewed
        - claim_data: Full claim details (status, damages, costs)
        - damages: List of damages with severity and costs
        - Any other relevant page state

        Example contexts:

        1. Customer viewing claim detail page:
        {
            "page": "claim_detail",
            "claim_id": 123,
            "claim_data": {
                "status": "approved",
                "total_cost": 2500.00,
                "damages": [
                    {"part": "Front Bumper", "severity": "moderate", "cost": 1200.00},
                    {"part": "Hood", "severity": "light", "cost": 1300.00}
                ]
            }
        }

        2. Customer viewing dashboard:
        {
            "page": "dashboard",
            "active_claims": 2,
            "pending_claims": 1
        }
        """
        context_parts = []

        if context.get('page'):
            context_parts.append(f"[CONTEXT: User is on the {context['page']} page]")

        if context.get('claim_id'):
            context_parts.append(f"[Current claim being viewed: #{context['claim_id']}]")

        if context.get('claim_data'):
            claim = context['claim_data']
            context_parts.append(f"[Claim details visible to user:")
            context_parts.append(f"  Status: {claim.get('status')}")
            context_parts.append(f"  Total Cost: ${claim.get('total_cost', 0):.2f}")

            if claim.get('damages'):
                context_parts.append(f"  Damages:")
                for dmg in claim['damages']:
                    context_parts.append(f"    - {dmg.get('part')}: {dmg.get('severity')} severity, ${dmg.get('cost', 0):.2f}")
            context_parts.append("]")

        return "\n".join(context_parts) if context_parts else "[No additional context]"
