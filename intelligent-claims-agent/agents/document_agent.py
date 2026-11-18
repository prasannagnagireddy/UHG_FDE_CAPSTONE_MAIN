from mcp_servers.documents_mcp import (
    classify_document_logic,
    extract_fields_logic,
    validate_case_documents_logic,
)


def analyze_documents(documents: list[dict]) -> dict:
    classified = []
    extracted = {}

    for d in documents:
        filename = d.get("filename", "document")
        text = d.get("text", "")

        result = classify_document_logic(filename, text)

        classified.append({
            "filename": filename,
            **result,
        })

        extracted[filename] = extract_fields_logic(text)

    types = [x["type"] for x in classified]

    validation = validate_case_documents_logic(types)

    low = [
        x["filename"]
        for x in classified
        if x.get("confidence", 0) < 0.55
    ]

    return {
        "agent": "document",
        "classified": classified,
        "extracted_fields": extracted,
        "missing_documents": validation["missing_documents"],
        "low_confidence_documents": low,
        "valid": validation["valid"] and not low,
    }