"""
Chatbot tools for database lookups and FAQ search.
"""
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ...models.claim import Claim
from ...models.customer import Customer
from ...models.damage import Damage
from ...database import SessionLocal
from ..llm.base import ToolDefinition

logger = logging.getLogger(__name__)


def get_chatbot_tools() -> List[ToolDefinition]:
    """
    Define tools available to the chatbot.

    Returns:
        List of ToolDefinition objects for LLM tool calling
    """
    return [
        ToolDefinition(
            name="get_claim_status",
            description="Retrieve the current status and details of a claim by claim_id",
            parameters={
                "type": "object",
                "properties": {
                    "claim_id": {
                        "type": "integer",
                        "description": "The claim ID to look up"
                    }
                },
                "required": ["claim_id"]
            }
        ),
        ToolDefinition(
            name="get_policy_details",
            description="Get policy information for a customer",
            parameters={
                "type": "object",
                "properties": {
                    "policy_number": {
                        "type": "string",
                        "description": "The policy number (optional, will use customer's active policy if not provided)"
                    }
                },
                "required": []
            }
        ),
        ToolDefinition(
            name="get_damage_details",
            description="Get detailed damage assessment for a specific claim",
            parameters={
                "type": "object",
                "properties": {
                    "claim_id": {
                        "type": "integer",
                        "description": "The claim ID to get damage details for"
                    }
                },
                "required": ["claim_id"]
            }
        ),
        ToolDefinition(
            name="search_faq",
            description="Search the FAQ knowledge base for answers to common questions",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question"
                    }
                },
                "required": ["query"]
            }
        )
    ]


async def execute_tool(tool_name: str, arguments: Dict[str, Any], customer_id: int, db: Session) -> str:
    """
    Execute a chatbot tool and return result as string.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from LLM
        customer_id: Current customer ID (for security check)
        db: Database session

    Returns:
        String result to pass back to LLM
    """
    logger.info(f"Executing tool: {tool_name} with args: {arguments}")

    try:
        if tool_name == "get_claim_status":
            return await _get_claim_status(arguments.get('claim_id'), customer_id, db)

        elif tool_name == "get_policy_details":
            return await _get_policy_details(arguments.get('policy_number'), customer_id, db)

        elif tool_name == "get_damage_details":
            return await _get_damage_details(arguments.get('claim_id'), customer_id, db)

        elif tool_name == "search_faq":
            return await _search_faq(arguments.get('query'))

        else:
            return f"Unknown tool: {tool_name}"

    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return f"Error executing tool: {str(e)}"


async def _get_claim_status(claim_id: int, customer_id: int, db: Session) -> str:
    """Get claim status and basic details"""
    if not claim_id:
        return "Please provide a claim ID."

    claim = db.query(Claim).filter(
        Claim.claim_id == claim_id,
        Claim.customer_id == customer_id
    ).first()

    if not claim:
        return f"Claim #{claim_id} not found or does not belong to you."

    status_map = {
        'pending_images': 'Pending - Waiting for images',
        'pending_review': 'Pending Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'appealed': 'Under Appeal'
    }

    status_text = status_map.get(claim.status, claim.status)

    result = f"""Claim #{claim_id} Status:
- Status: {status_text}
- Filed: {claim.fnol_date.strftime('%B %d, %Y') if claim.fnol_date else 'N/A'}
- Estimated Amount: ${claim.estimated_claim_amount:.2f if claim.estimated_claim_amount else 0}
- Policy: {claim.policy_number}
- Decision: {claim.decision or 'Pending'}
"""

    if claim.decision_explanation:
        result += f"- Explanation: {claim.decision_explanation}\n"

    return result


async def _get_policy_details(policy_number: str, customer_id: int, db: Session) -> str:
    """Get policy details for customer"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        return "Customer not found."

    # If no policy number provided, use customer's default policy
    if not policy_number:
        policy_number = customer.policy_number

    result = f"""Policy Information:
- Policy Number: {customer.policy_number}
- Policy Type: {customer.policy_type or 'Standard Auto'}
- Coverage: {customer.coverage_type or 'Full Coverage'}
- Premium: ${customer.premium_amount:.2f if customer.premium_amount else 0}/month
- Deductible: ${customer.deductible:.2f if customer.deductible else 500}
- Policy Status: Active
"""

    return result


async def _get_damage_details(claim_id: int, customer_id: int, db: Session) -> str:
    """Get detailed damage assessment for a claim"""
    if not claim_id:
        return "Please provide a claim ID."

    # Verify claim belongs to customer
    claim = db.query(Claim).filter(
        Claim.claim_id == claim_id,
        Claim.customer_id == customer_id
    ).first()

    if not claim:
        return f"Claim #{claim_id} not found or does not belong to you."

    damages = db.query(Damage).filter(Damage.claim_id == claim_id).all()

    if not damages:
        return f"No damage details found for claim #{claim_id}."

    result = f"Damage Details for Claim #{claim_id}:\n\n"

    for i, damage in enumerate(damages, 1):
        result += f"{i}. {damage.damage_part or 'Unknown Part'}\n"
        result += f"   - Severity: {damage.severity or 'Unknown'}\n"
        result += f"   - Repair Cost: ${damage.estimated_total_cost:.2f if damage.estimated_total_cost else 0}\n"
        result += f"   - Labor: {damage.labor_hours:.1f if damage.labor_hours else 0} hours @ ${damage.labor_rate:.2f if damage.labor_rate else 0}/hr\n"
        result += f"   - Parts: ${damage.estimated_parts_cost:.2f if damage.estimated_parts_cost else 0}\n"

        if damage.repair_recommendation:
            result += f"   - Recommendation: {damage.repair_recommendation}\n"

        result += "\n"

    total = sum(d.estimated_total_cost or 0 for d in damages)
    result += f"Total Estimated Repair Cost: ${total:.2f}"

    return result


async def _search_faq(query: str) -> str:
    """Search FAQ knowledge base using keyword matching"""
    if not query:
        return "Please provide a search query."

    try:
        # Load FAQ from markdown file
        import os
        faq_path = os.path.join(os.path.dirname(__file__), '../../../..', 'data', 'customer-faq.md')

        if not os.path.exists(faq_path):
            logger.warning(f"FAQ file not found at {faq_path}")
            return "FAQ knowledge base not available at this time."

        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_content = f.read()

        # Parse FAQ markdown
        faqs = _parse_faq_markdown(faq_content)

        # Simple keyword matching
        query_lower = query.lower()
        matches = []

        for faq in faqs:
            # Check if query keywords match FAQ keywords or question
            score = 0

            # Check question match
            if query_lower in faq['question'].lower():
                score += 10

            # Check keyword match
            for keyword in faq.get('keywords', []):
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    score += 5

            # Check category match
            if query_lower in faq['category'].lower():
                score += 3

            if score > 0:
                matches.append((score, faq))

        # Sort by score and take top 3
        matches.sort(key=lambda x: x[0], reverse=True)
        top_matches = matches[:3]

        if not top_matches:
            return f"No FAQ entries found matching '{query}'. Please try rephrasing your question or ask me directly."

        result = "Here's what I found in our FAQ:\n\n"
        for score, faq in top_matches:
            result += f"**Q: {faq['question']}**\n"
            result += f"A: {faq['answer']}\n\n"

        return result

    except Exception as e:
        logger.error(f"FAQ search failed: {e}", exc_info=True)
        return "Sorry, I'm having trouble searching the FAQ right now. Please ask your question directly and I'll do my best to help."


def _parse_faq_markdown(content: str) -> List[Dict[str, Any]]:
    """
    Parse FAQ markdown file into structured data.

    Expected format:
    ## Category Name

    ### Question?
    Answer text here.

    **Keywords:** keyword1, keyword2

    Args:
        content: Markdown file content

    Returns:
        List of FAQ dictionaries with question, answer, category, keywords
    """
    faqs = []
    lines = content.split('\n')

    current_category = ""
    current_question = ""
    current_answer = []
    current_keywords = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Category header (## )
        if line.startswith('## ') and not line.startswith('###'):
            current_category = line[3:].strip()

        # Question header (### )
        elif line.startswith('### '):
            # Save previous FAQ if exists
            if current_question and current_answer:
                faqs.append({
                    'category': current_category,
                    'question': current_question,
                    'answer': '\n'.join(current_answer).strip(),
                    'keywords': current_keywords
                })

            # Start new FAQ
            current_question = line[4:].strip()
            current_answer = []
            current_keywords = []

        # Keywords line
        elif line.startswith('**Keywords:**'):
            keywords_text = line.replace('**Keywords:**', '').strip()
            current_keywords = [k.strip() for k in keywords_text.split(',')]

        # Answer text (non-empty, not a header, not keywords)
        elif line and not line.startswith('#') and not line.startswith('**Keywords:**') and not line.startswith('---'):
            if current_question:  # Only collect if we have a question
                current_answer.append(line)

        i += 1

    # Save last FAQ
    if current_question and current_answer:
        faqs.append({
            'category': current_category,
            'question': current_question,
            'answer': '\n'.join(current_answer).strip(),
            'keywords': current_keywords
        })

    return faqs
