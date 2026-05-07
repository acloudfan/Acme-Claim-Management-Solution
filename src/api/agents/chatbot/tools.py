"""
Chatbot tools for database lookups and FAQ search.
"""
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ...models.claim import Claim
from ...models.customer import Customer
from ...models.damage import Damage
from ...models.vehicle import Vehicle
from ...models.policy import Policy, PolicyVehicle
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
            name="get_customer_info",
            description="Get customer's personal information including name, contact details, and active policies. Use this at the start of conversation to greet customer by name.",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        ToolDefinition(
            name="list_customer_policies",
            description="List all active policies for the customer with details about coverage, premiums, and vehicles",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        ToolDefinition(
            name="list_customer_claims",
            description="List all claims for the customer, sorted by date (most recent first). Use this to find the most recent claim, count claims, or show claim history.",
            parameters={
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "description": "Optional filter by status (e.g., 'approved', 'pending_review', 'rejected', 'appealed')",
                        "enum": ["all", "approved", "pending_review", "rejected", "appealed", "pending_images"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of claims to return (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        ToolDefinition(
            name="get_claim_status",
            description="Retrieve detailed status and information for a specific claim by claim_id",
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
            description="Get detailed information for a specific policy by policy number",
            parameters={
                "type": "object",
                "properties": {
                    "policy_number": {
                        "type": "string",
                        "description": "The policy number to look up"
                    }
                },
                "required": ["policy_number"]
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
        if tool_name == "get_customer_info":
            return await _get_customer_info(customer_id, db)

        elif tool_name == "list_customer_policies":
            return await _list_customer_policies(customer_id, db)

        elif tool_name == "list_customer_claims":
            return await _list_customer_claims(
                customer_id,
                db,
                arguments.get('status_filter', 'all'),
                arguments.get('limit', 10)
            )

        elif tool_name == "get_claim_status":
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


async def _get_customer_info(customer_id: int, db: Session) -> str:
    """Get customer's personal information"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        return "Customer not found."

    # Count active policies and claims
    from ...models.policy import Policy
    policies = db.query(Policy).filter(Policy.customer_id == customer_id).all()
    claims = db.query(Claim).filter(Claim.customer_id == customer_id).all()
    active_claims = [c for c in claims if not c.claim_closed]

    result = f"""Customer Information:
- Name: {customer.fname} {customer.lname}
- Customer ID: {customer_id}
- Email: {customer.email or 'Not on file'}
- Phone: {customer.phone or 'Not on file'}
- Address: {customer.address or 'Not on file'}
- State: {customer.state or 'Not on file'}
- Active Policies: {len(policies)}
- Total Claims: {len(claims)}
- Active Claims: {len(active_claims)}
"""

    return result


async def _list_customer_policies(customer_id: int, db: Session) -> str:
    """List all policies for the customer"""
    from ...models.policy import Policy, PolicyVehicle
    from ...models.vehicle import Vehicle

    policies = db.query(Policy).filter(Policy.customer_id == customer_id).all()

    if not policies:
        return "No active policies found for your account."

    result = f"You have {len(policies)} active {'policy' if len(policies) == 1 else 'policies'}:\n\n"

    for i, policy in enumerate(policies, 1):
        result += f"{i}. **Policy #{policy.policy_number}**\n"
        result += f"   - Policyholder: {policy.policyholder_name}\n"
        result += f"   - Coverage Period: {policy.start_date.strftime('%m/%d/%Y')} to {policy.end_date.strftime('%m/%d/%Y')}\n"
        result += f"   - Premium: ${policy.premium:.2f}/month\n"
        result += f"   - Deductible: ${policy.deductible:.2f}\n"
        result += f"   - Bodily Injury Limit: ${policy.bodily_injury_limit:,.2f}\n"
        result += f"   - Property Damage Limit: ${policy.property_damage_limit:,.2f}\n"

        # Get vehicles covered under this policy
        policy_vehicles = db.query(PolicyVehicle).filter(
            PolicyVehicle.policy_number == policy.policy_number
        ).all()

        if policy_vehicles:
            result += f"   - Covered Vehicles:\n"
            for pv in policy_vehicles:
                vehicle = db.query(Vehicle).filter(Vehicle.vin == pv.vin).first()
                if vehicle:
                    result += f"     • {vehicle.year} {vehicle.make} {vehicle.model} (VIN: {vehicle.vin[-6:]}...)\n"

        if policy.additional_insured_1:
            result += f"   - Additional Insured: {policy.additional_insured_1}"
            if policy.additional_insured_2:
                result += f", {policy.additional_insured_2}"
            if policy.additional_insured_3:
                result += f", {policy.additional_insured_3}"
            result += "\n"

        result += "\n"

    return result


async def _list_customer_claims(customer_id: int, db: Session, status_filter: str = 'all', limit: int = 10) -> str:
    """List all claims for the customer, sorted by most recent first"""

    # Build query
    query = db.query(Claim).filter(Claim.customer_id == customer_id)

    # Apply status filter if not 'all'
    if status_filter and status_filter != 'all':
        query = query.filter(Claim.current_status == status_filter)

    # Sort by most recent first and limit
    claims = query.order_by(Claim.fnol_date.desc()).limit(limit).all()

    if not claims:
        if status_filter and status_filter != 'all':
            return f"No claims found with status '{status_filter}'."
        return "You don't have any claims on file."

    # Status mapping for better readability
    status_map = {
        'draft': 'Draft',
        'pending_images': 'Pending - Waiting for Images',
        'pending_review': 'Pending Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'appealed': 'Under Appeal',
        'closed': 'Closed'
    }

    result = f"You have {len(claims)} claim{'s' if len(claims) != 1 else ''}"
    if status_filter and status_filter != 'all':
        result += f" with status '{status_filter}'"
    result += ":\n\n"

    for i, claim in enumerate(claims, 1):
        status_text = status_map.get(claim.current_status, claim.current_status)

        result += f"{i}. **Claim #{claim.claim_id}**\n"
        result += f"   - Status: {status_text}\n"
        result += f"   - Filed: {claim.fnol_date.strftime('%B %d, %Y') if claim.fnol_date else 'N/A'}\n"
        result += f"   - Date of Damage: {claim.date_of_damage.strftime('%B %d, %Y') if claim.date_of_damage else 'N/A'}\n"
        result += f"   - Vehicle: {claim.vin[-6:] if claim.vin else 'N/A'}\n"
        result += f"   - Policy: {claim.policy_number}\n"

        # Add claim amount if available
        if claim.claim_amount:
            result += f"   - Claim Amount: ${claim.claim_amount:.2f}\n"

        # Add closed date if closed
        if claim.claim_closed and claim.claim_closed_date:
            result += f"   - Closed: {claim.claim_closed_date.strftime('%B %d, %Y')}\n"

        # Add routing info if routed to traditional
        if claim.routed_to_traditional:
            result += f"   - Routed to Traditional Processing\n"
            if claim.reason_routing_to_traditional:
                result += f"     Reason: {claim.reason_routing_to_traditional}\n"

        # Add appeal info if appealed
        if claim.appeal_count and claim.appeal_count > 0:
            result += f"   - Appeals: {claim.appeal_count}\n"

        result += "\n"

    # Add helpful tip
    if len(claims) > 0:
        result += f"💡 Tip: For detailed information about a specific claim, ask 'What's the status of claim #{claims[0].claim_id}?'"

    return result


async def _get_claim_status(claim_id: int, customer_id: int, db: Session) -> str:
    """Get claim status and detailed information"""
    if not claim_id:
        return "Please provide a claim ID."

    claim = db.query(Claim).filter(
        Claim.claim_id == claim_id,
        Claim.customer_id == customer_id
    ).first()

    if not claim:
        return f"Claim #{claim_id} not found or does not belong to you."

    status_map = {
        'draft': 'Draft',
        'pending_images': 'Pending - Waiting for Images',
        'pending_review': 'Pending Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'appealed': 'Under Appeal',
        'closed': 'Closed'
    }

    status_text = status_map.get(claim.current_status, claim.current_status)

    result = f"""Claim #{claim_id} Details:

**Status**: {status_text}
**Filed**: {claim.fnol_date.strftime('%B %d, %Y') if claim.fnol_date else 'N/A'}
**Date of Damage**: {claim.date_of_damage.strftime('%B %d, %Y') if claim.date_of_damage else 'N/A'}
**Vehicle**: VIN ending in {claim.vin[-6:] if claim.vin else 'N/A'}
**Policy**: {claim.policy_number}
**Drivable**: {'Yes' if claim.is_drivable else 'No'}
"""

    if claim.claim_amount:
        result += f"**Claim Amount**: ${claim.claim_amount:.2f}\n"

    if claim.actual_claim_amount:
        result += f"**Actual Amount Paid**: ${claim.actual_claim_amount:.2f}\n"

    if claim.ai_estimate_accepted:
        result += "**AI Estimate**: Accepted by customer\n"

    if claim.routed_to_traditional:
        result += f"\n**Note**: This claim was routed to traditional processing.\n"
        if claim.reason_routing_to_traditional:
            result += f"**Reason**: {claim.reason_routing_to_traditional}\n"

    if claim.assigned_adjustor_id:
        result += f"**Assigned Adjustor**: {claim.assigned_adjustor_id}\n"

    # Appeal information
    if claim.appeal_count and claim.appeal_count > 0:
        result += f"\n**Appeals Filed**: {claim.appeal_count}\n"
        if claim.first_appeal_reason:
            result += f"**First Appeal Reason**: {claim.first_appeal_reason}\n"
            result += f"**First Appeal Date**: {claim.first_appeal_date.strftime('%B %d, %Y') if claim.first_appeal_date else 'N/A'}\n"
        if claim.appeal_count > 1 and claim.second_appeal_reason:
            result += f"**Second Appeal Reason**: {claim.second_appeal_reason}\n"
            result += f"**Second Appeal Date**: {claim.second_appeal_date.strftime('%B %d, %Y') if claim.second_appeal_date else 'N/A'}\n"

    # Incident description
    if claim.incident_description:
        result += f"\n**Incident Description**:\n{claim.incident_description}\n"

    # Closed information
    if claim.claim_closed:
        result += f"\n**Claim Closed**: {claim.claim_closed_date.strftime('%B %d, %Y') if claim.claim_closed_date else 'Yes'}\n"

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
