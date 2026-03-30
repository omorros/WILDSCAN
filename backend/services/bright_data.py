import asyncio
import json
import shutil

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from backend.config import settings


class BrightDataMCP:
    """Real MCP client connecting to Bright Data's @brightdata/mcp server."""

    def __init__(self):
        self.api_token = settings.bright_data_api_token
        self._npx_path = shutil.which("npx") or "npx"

    def _server_params(self) -> StdioServerParameters:
        return StdioServerParameters(
            command=self._npx_path,
            args=["-y", "@brightdata/mcp"],
            env={"API_TOKEN": self.api_token, "PRO_MODE": "true"},
        )

    async def scrape_as_html(self, url: str) -> str:
        """Call the scrape_as_html MCP tool — returns raw HTML."""
        result = await self._call_tool("scrape_as_html", {"url": url})
        return result

    async def scrape_as_markdown(self, url: str) -> str:
        """Call the scrape_as_markdown MCP tool — returns cleaned markdown."""
        result = await self._call_tool("scrape_as_markdown", {"url": url})
        return result

    async def search_engine(self, query: str) -> str:
        """Call the search_engine MCP tool."""
        result = await self._call_tool("search_engine", {"query": query})
        return result

    async def list_tools(self) -> list[str]:
        """List all available MCP tools from the server."""
        async with stdio_client(self._server_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [t.name for t in tools.tools]

    async def _call_tool(self, tool_name: str, arguments: dict) -> str:
        """Connect to MCP server, call a tool, return the text result."""
        async with stdio_client(self._server_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                # MCP returns content blocks — extract text
                texts = []
                for block in result.content:
                    if hasattr(block, "text"):
                        texts.append(block.text)
                return "\n".join(texts)


bright_data = BrightDataMCP()
