def test_policy_demo_coverage():
    from mcp_servers.policy_mcp import check_coverage
    assert check_coverage('AUTO-DEMO','collision',10000)['human_review_required'] is True
def test_field_extract_amount():
    from mcp_servers.documents_mcp import extract_fields
    assert extract_fields('Claim amount: 12000')['claim_amount'] is not None
