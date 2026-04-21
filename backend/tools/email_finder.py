import os
import re
import requests


def _guess_domain(company_name: str) -> str:
    """Turn 'ServiceNow' → 'servicenow.com'"""
    slug = re.sub(r'[^a-z0-9]', '', company_name.lower())
    return f"{slug}.com"


def find_email_for_company(company_name: str) -> str | None:
    """
    Use Hunter.io Domain Search API to find an email for a given company.
    Tries guessed domain first, then Hunter's autocomplete as fallback.
    Returns the best email found, or None.
    """
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key or api_key == "your_hunter_api_key_here":
        return None

    domains_to_try = []

    # Primary: guess domain directly from company name
    domains_to_try.append(_guess_domain(company_name))

    # Fallback: Hunter autocomplete
    try:
        ac = requests.get(
            "https://api.hunter.io/v2/domains/autocomplete",
            params={"query": company_name, "api_key": api_key},
            timeout=8,
        )
        for d in ac.json().get("data", {}).get("domains", [])[:3]:
            domain = d.get("domain")
            if domain and domain not in domains_to_try:
                domains_to_try.append(domain)
    except Exception:
        pass

    priority_roles = {"ceo", "cto", "founder", "co-founder", "vp", "director", "head", "president"}

    for domain in domains_to_try:
        try:
            resp = requests.get(
                "https://api.hunter.io/v2/domain-search",
                params={"domain": domain, "api_key": api_key, "limit": 10},
                timeout=8,
            )
            emails = resp.json().get("data", {}).get("emails", [])
            if not emails:
                continue

            # Prefer decision-maker roles
            for entry in emails:
                position = (entry.get("position") or "").lower()
                if any(role in position for role in priority_roles):
                    return entry.get("value")

            # Fallback to first verified email
            for entry in emails:
                if entry.get("confidence", 0) >= 70:
                    return entry.get("value")

            # Last resort: first email
            return emails[0].get("value")

        except Exception:
            continue

    return None
