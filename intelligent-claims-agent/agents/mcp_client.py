import asyncio
import os
import sys
import threading
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

_CLIENT = None
_TOOLS = None
_INIT_LOCK = threading.Lock()


def _initialize():
    global _CLIENT, _TOOLS

    if _TOOLS is not None:
        return

    with _INIT_LOCK:
        if _TOOLS is not None:
            return

        root = Path(__file__).resolve().parent.parent

        server_files = {
            "case": "case_mcp.py",
            "documents": "documents_mcp.py",
            "policy": "policy_mcp.py",
            "workflow": "workflow_mcp.py",
        }

        connections = {
            name: {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    str(root / "mcp_servers" / filename)
                ],
                "env": {
                    **os.environ,
                    "PYTHONPATH": str(root),
                },
            }
            for name, filename in server_files.items()
        }

        client = MultiServerMCPClient(
            connections,
            tool_name_prefix=True,
        )

        tools = asyncio.run(client.get_tools())

        _CLIENT = client
        _TOOLS = {
            tool.name: tool
            for tool in tools
        }


def get_tool(name: str):
    _initialize()

    if name not in _TOOLS:
        raise KeyError(
            f"MCP tool not found: {name}"
        )

    return _TOOLS[name]


async def _async_call_tool(name: str, arguments: dict):
    tool = get_tool(name)
    return await tool.ainvoke(arguments)


def call_tool(name: str, arguments: dict):
    """
    Sync-compatible MCP tool caller.
    Executes async MCP tools safely.
    """

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No active event loop in this thread
        return asyncio.run(
            _async_call_tool(name, arguments)
        )

    # If an event loop is already running,
       # run the coroutine in a separate thread.
    result = {}
    error = {}

    def worker():
        try:
            result["value"] = asyncio.run(
                _async_call_tool(name, arguments)
            )
        except Exception as exc:
            error["exception"] = exc

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    if "exception" in error:
        raise error["exception"]

    return result.get("value")


def list_tool_names():
    _initialize()
    return sorted(_TOOLS.keys())