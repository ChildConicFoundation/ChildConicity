"""ChildConicity MCP server."""

from mcp.server.mcpserver import MCPServer

from src.mcp_server.mcp_preconditions import check_preconditions as run_precondition_checks


def build_server():
    server = MCPServer("childconicity")

    @server.tool()
    def check_preconditions(project_root: str = ".") -> dict:
        """Verify ratings, processed corpora, types output, and plot libraries before an analysis run."""
        return run_precondition_checks(project_root)

    return server


def main():
    build_server().run()
