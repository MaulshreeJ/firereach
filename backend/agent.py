from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.email_sender import tool_outreach_automated_sender
from tools.email_finder import find_email_for_company

def run_agent(icp: str, company: str, recipient_email: str) -> dict:
    """
    Execute the full FireReach pipeline.
    If recipient_email is empty, Hunter.io is used to auto-find one.
    """
    # Auto-find email via Hunter if not provided
    if not recipient_email or not recipient_email.strip():
        found = find_email_for_company(company)
        recipient_email = found or ""
    
    # Step 1: Harvest signals
    signals = tool_signal_harvester(company)
    
    # Step 2: Generate account brief
    research = tool_research_analyst(
        company=company,
        signals=signals["signals"],
        icp=icp
    )
    
    # Step 3: Generate and send email
    email_result = tool_outreach_automated_sender(
        account_brief=research["account_brief"],
        signals=signals["signals"],
        recipient_email=recipient_email,
        company=company
    )
    
    return {
        "signals": signals["signals"],
        "account_brief": research["account_brief"],
        "generated_email": email_result.get("generated_email", ""),
        "subject": email_result.get("subject", ""),
        "status": email_result.get("status", "failed"),
        "recipient": email_result.get("recipient", recipient_email)
    }
