from mcp_servers._compat import FastMCP
import re

mcp = FastMCP("documents-mcp")


# -------- Normal Python functions for local agents/tests --------

def classify_document_logic(filename: str, text: str) -> dict:
    """Classify a claim document using simple lexical signals."""
    content = (filename + " " + text).lower()

    categories = {
        "claim_form": ["claim form", "claimant", "claim number"],
        "invoice": ["invoice", "estimate", "total due"],
        "medical_report": ["medical report", "diagnosis", "doctor"],
        "police_report": ["police report", "incident report"],
        "photo": ["photo", "image", "damage"],
    }

    scores = {
        key: sum(term in content for term in terms)
        for key, terms in categories.items()
    }

    winner = max(scores, key=scores.get)
    confidence = (
        min(0.95, 0.5 + 0.1 * scores[winner])
        if scores[winner] else 0.2
    )

    return {
        "type": winner if scores[winner] else "unknown",
        "confidence": confidence,
        "scores": scores,
    }


def extract_fields_logic(text: str) -> dict:
    """Extract basic labeled fields from claim document text."""

    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    return {
        "claimant_name": find(
            r"(?:claimant|name)\s*[:=-]\s*([^\n]+)"
        ),
        "policy_number": find(
            r"policy(?:\s+number)?\s*[:=-]\s*([A-Za-z0-9-]+)"
        ),
        "claim_amount": find(
            r"(?:claim amount|amount|total)\s*[:=-]\s*([$₹]?\s*[0-9,.]+)"
        ),
        "incident_date": find(
            r"incident date\s*[:=-]\s*([^\n]+)"
        ),
    }


# Plain Python callable (used by pytest and agents)
def extract_fields(text: str) -> dict:
    return extract_fields_logic(text)


def validate_case_documents_logic(document_types: list) -> dict:
    """Check required demo claim documents."""
    required = {"claim_form", "invoice", "photo"}
    present = set(document_types)
    missing = sorted(required - present)

    return {
        "valid": not missing,
        "missing_documents": missing,
        "confidence": "demo rules",
    }


# -------- MCP tool wrappers --------

@mcp.tool()
def list_documents(case_id: str) -> list:
    """List registered documents for this demo server."""
    return []


@mcp.tool()
def extract_text(filename: str, content_text: str) -> dict:
    """Demo text-first extraction."""
    return {
        "filename": filename,
        "text": content_text.strip(),
        "chars": len(content_text),
    }


@mcp.tool()
def classify_document(filename: str, text: str) -> dict:
    """MCP tool for document classification."""
    return classify_document_logic(filename, text)


@mcp.tool(name="extract_fields")
def extract_fields_tool(text: str) -> dict:
    """MCP tool for extracting document fields."""
    return extract_fields_logic(text)


@mcp.tool()
def validate_case_documents(document_types: list) -> dict:
    """MCP tool for validating required claim documents."""
    return validate_case_documents_logic(document_types)


if __name__ == "__main__":
    mcp.run(transport="stdio")