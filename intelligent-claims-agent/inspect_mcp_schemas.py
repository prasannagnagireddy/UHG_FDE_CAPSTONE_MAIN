import asyncio, os, sys, json
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

root = Path.cwd()
files = {
    "case": "case_mcp.py",
    "documents": "documents_mcp.py",
    "policy": "policy_mcp.py",
    "workflow": "workflow_mcp.py",
}

cfg = {
    name: {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(root / "mcp_servers" / filename)],
        "env": {**os.environ, "PYTHONPATH": str(root)}
    }
    for name, filename in files.items()
}

def get_schema(tool):
    schema = tool.args_schema
    if hasattr(schema, "model_json_schema"):
        return schema.model_json_schema()
    if isinstance(schema, dict):
        return schema
    if hasattr(tool, "tool_call_schema"):
        model = tool.tool_call_schema
        if hasattr(model, "model_json_schema"):
            return model.model_json_schema()
    return str(schema)

async def main():
    client = MultiServerMCPClient(cfg, tool_name_prefix=True)
    tools = await client.get_tools()

    print("=== MCP TOOL SCHEMAS ===")
    for tool in sorted(tools, key=lambda t: t.name):
        print(f"\n--- {tool.name} ---")
        print(json.dumps(get_schema(tool), indent=2, default=str))

asyncio.run(main())
