
from mcp_servers._compat import FastMCP

mcp = FastMCP("policy-mcp")

# Synthetic demo policy catalog
POLICIES = {
    "AUTO-DEMO": {
        "policy_id": "AUTO-DEMO",
        "coverage": ["collision", "comprehensive", "glass"],
        "exclusions": ["intentional damage", "wear and tear"],
        "max_demo_limit": 500000,
    }
}


# ---------- Normal Python functions ----------

def get_policy_logic(policy_id: str) -> dict:
    return POLICIES.get(
        policy_id.upper(),
        {"found": False, "policy_id": policy_id}
    )


def check_coverage_logic(
    policy_id: str,
    claim_type: str,
    claim_amount: float
) -> dict:
    """Normal Python function for agents and tests."""

    policy = POLICIES.get(policy_id.upper())

    if not policy:
        return {
            "coverage": "unknown",
            "reason": "Policy not found in demo catalog",
            "human_review_required": True,
        }

    covered = claim_type.lower() in [
        item.lower() for item in policy["coverage"]
    ]

    within_limit = claim_amount <= policy["max_demo_limit"]

    return {
        "coverage": (
            "potentially_covered"
            if covered and within_limit
            else "flagged"
        ),
        "covered_type": covered,
        "within_demo_limit": within_limit,
        "policy_reference": policy_id,
        "human_review_required": True,
    }


# Compatibility function used by tests
def check_coverage(
    policy_id: str,
    claim_type: str,
    claim_amount: float
) -> dict:
    return check_coverage_logic(
        policy_id, claim_type, claim_amount
    )


def search_policy_wording_logic(query: str) -> list:
    terms = query.lower().split()

    snippets = [
        {
            "policy_id": "AUTO-DEMO",
            "text": (
                "Demo auto policy lists collision, comprehensive "
                "and glass as sample coverages. Wear and tear and "
                "intentional damage are demo exclusions."
            ),
        }
    ]

    matches = [
        item for item in snippets
        if any(term in item["text"].lower() for term in terms)
    ]

    return matches or snippets


# ---------- MCP tool wrappers ----------

@mcp.tool()
def get_policy(policy_id: str) -> dict:
    """Return synthetic policy details."""
    return get_policy_logic(policy_id)


@mcp.tool(name="check_coverage")
def check_coverage_tool(
    policy_id: str,
    claim_type: str,
    claim_amount: float
) -> dict:
    """MCP tool for synthetic policy coverage check."""
    return check_coverage_logic(
        policy_id, claim_type, claim_amount
    )


@mcp.tool()
def search_policy_wording(query: str) -> list:
    """Search synthetic policy wording."""
    return search_policy_wording_logic(query)


@mcp.tool()
def search_policy(query: str) -> list:
    """Alias for policy wording search."""
    return search_policy_wording_logic(query)


if __name__ == "__main__":
    mcp.run(transport="stdio")
