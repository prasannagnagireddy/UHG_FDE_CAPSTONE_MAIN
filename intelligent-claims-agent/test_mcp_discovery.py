import asyncio
import os
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

root = Path.cwd()
python = sys.executable

server_files = {
    "case": "case_mcp.py",
    "documents": "documents_mcp.py",
    "policy": "policy_mcp.py",
    "workflow": "workflow_mcp.py",
}

connections = {}
for name, filename in server_files.items():
    connections[name] = {
        "transport": "stdio",
        "command": python,
        "args": [str(root / "mcp_servers" / filename)],
        "env": {**os.environ, "PYTHONPATH": str(root)}
    }

async def main():
    client = MultiServerMCPClient(connections, tool_name_prefix=True)
    tools = await client.get_tools()

    print("\n=== REAL MCP DISCOVERY RESULT ===")
    for tool in sorted(tools, key=lambda t: t.name):
        print(f"OK: {tool.name}")
    print(f"\nREAL TOTAL: {len(tools)} tools")

asyncio.run(main())
