"""Errors the MCP client is meant to read."""

from mcp.server.mcpserver.exceptions import ToolError as ProtocolToolError


class ToolError(ProtocolToolError):
    """A pipeline failure with a message the caller can act on."""
