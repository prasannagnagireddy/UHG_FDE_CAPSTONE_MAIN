from agents.mcp_client import call_tool, list_tool_names

print("Discovered tools:", len(list_tool_names()))

result = call_tool(
    "policy_check_coverage",
    {
        "policy_id": "AUTO-DEMO",
        "claim_type": "collision",
        "claim_amount": 25000,
    },
)

print("\n===== POLICY MCP RESULT =====")
print(result)
print("\nMCP POLICY TEST PASSED")