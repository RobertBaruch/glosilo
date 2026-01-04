"""MCP server for the glosilo lookup tool."""

from fastmcp import FastMCP
from glosilo import lookup

mcp = FastMCP("Glosilo MCP Server")


@mcp.tool
def eo_lookup(words: str) -> lookup.Results:
    return lookup.convert_to_results(lookup.lookup_words(words))


if __name__ == "__main__":
    mcp.run()
