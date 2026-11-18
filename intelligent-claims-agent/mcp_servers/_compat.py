"""Test-friendly fallback when FastMCP isn't installed; actual servers need FastMCP."""
try:
    from fastmcp import FastMCP as FastMCP
except ImportError:
    class FastMCP:
        def __init__(self, name): self.name=name
        def tool(self, *args, **kwargs):
            def decorate(fn): return fn
            return decorate
        def run(self, *args, **kwargs):
            raise RuntimeError('FastMCP is required to launch MCP servers. Install requirements.txt')
