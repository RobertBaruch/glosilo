"""Simple tests for the MCP server."""

import asyncio

from fastmcp import Client

# First run the server as:
# fastmcp run src/glosilo/mcp_server.py:mcp --transport http --port 8000

client = Client("http://localhost:8000/mcp")

async def call_tool(words: str):
    async with client:
        result = await client.call_tool("eo_lookup", {"words": words})
        print(result)

asyncio.run(call_tool("parolanto"))
