"""Stdio MCP server. The protocol owns stdout; pipeline logs go to stderr."""

from typing import Annotated

import anyio
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError
from pydantic import Field

from src import __version__
from src.gui.services import (
    DEFAULT_ICONICITY_CSV,
    DEFAULT_RATED_OUTPUT_DIR,
    DEFAULT_TOKENS_OUTPUT_DIR,
    DEFAULT_TYPE_COUNT_MODE,
    DEFAULT_TYPES_OUTPUT_DIR,
)
from src.mcp_server.errors import ToolError
from src.mcp_server import tools

INSTRUCTIONS = (
    "ChildConicity analyzes iconicity in CHILDES/TalkBank corpora. "
    "Pipeline: download_iconicity_ratings, download_corpora, "
    "normalize_corpora, analyze_types, export_rated. "
    "analyze_tokens is optional. Always pass an explicit corpora list. "
    "Never ask for a TalkBank password; the server reads "
    "CHILDCONICITY_TALKBANK_USER and CHILDCONICITY_TALKBANK_PASSWORD. "
    "Analysis tools return a short summary. Read "
    "childconicity://results/{name} for the full path map. "
    "The result name is the file name at the end of result_file."
)


def build_server() -> MCPServer:
    server = MCPServer(
        name="childconicity",
        instructions=INSTRUCTIONS,
        version=__version__,
    )

    @server.tool(structured_output=False)
    async def check_preconditions(ctx: Context) -> dict:
        """Check local files and whether TalkBank credentials are set.

        Returns booleans only. It does not return credential values.
        """
        return await _in_thread(ctx, "Checking preconditions", tools.check_preconditions)

    @server.tool(structured_output=False)
    async def list_corpora(
        ctx: Context, processed_root: str = "Corpora_modified"
    ) -> dict:
        """List normalized corpus names under Corpora_modified."""
        return await _in_thread(
            ctx, "Listing corpora", tools.list_corpora, processed_root
        )

    @server.tool(structured_output=False)
    async def list_categories(
        ctx: Context, processed_root: str = "Corpora_modified"
    ) -> dict:
        """List grammatical categories accepted by analyze_types."""
        return await _in_thread(
            ctx, "Listing categories", tools.list_categories, processed_root
        )

    @server.tool(structured_output=False)
    async def download_iconicity_ratings(ctx: Context, force: bool = False) -> dict:
        """Download iconicity ratings from OSF unless the CSV already exists."""
        return await _in_thread(
            ctx,
            "Downloading iconicity ratings",
            tools.download_iconicity_ratings,
            force,
        )

    @server.tool(structured_output=False)
    async def download_corpora(
        corpora: Annotated[list[str], Field(min_length=1)],
        ctx: Context,
        force: bool = False,
    ) -> dict:
        """Download TalkBank CHILDES corpora with headless Chrome.

        This step needs Chrome and Selenium and can take a long time.
        Credentials are read from CHILDCONICITY_TALKBANK_USER and
        CHILDCONICITY_TALKBANK_PASSWORD. This tool has no password argument.
        """

        def _run() -> dict:
            def _on_corpus(name: str, index: int, total: int) -> None:
                _report_from_thread(ctx, index, total, f"Downloading {name}")

            return tools.download_corpora(corpora, force=force, on_corpus=_on_corpus)

        await _safe_progress(ctx, 0, max(len(corpora), 1), "Starting TalkBank download")
        return await _in_thread(ctx, "Downloading corpora", _run, report_start=False)

    @server.tool(structured_output=False)
    async def normalize_corpora(
        ctx: Context,
        source_root: str = "Corpora",
        output_root: str = "Corpora_modified",
    ) -> dict:
        """Normalize downloaded TalkBank corpora into Corpora_modified."""

        def _run() -> dict:
            def _on_corpus(name: str, index: int, total: int) -> None:
                _report_from_thread(ctx, index, total, f"Normalizing {name}")

            return tools.normalize_corpora(
                source_root=source_root,
                output_root=output_root,
                on_corpus=_on_corpus,
            )

        await _safe_progress(ctx, 0, len(tools.NORMALIZE_STEPS), "Starting normalization")
        return await _in_thread(ctx, "Normalizing corpora", _run, report_start=False)

    @server.tool(structured_output=False)
    async def analyze_tokens(
        corpora: Annotated[list[str], Field(min_length=1)],
        ctx: Context,
        generate_plots: bool = False,
        processed_root: str = "Corpora_modified",
        output_dir: str = DEFAULT_TOKENS_OUTPUT_DIR,
        iconicity_csv: str = DEFAULT_ICONICITY_CSV,
    ) -> dict:
        """Run the token analysis for the named corpora.

        corpora must contain one or more names from list_corpora.
        The reply is a short summary. The full path map stays on disk.
        """
        await _safe_progress(ctx, 0, 3, "Checking corpora")
        await _in_thread(
            ctx,
            "Checking corpora",
            tools.prepare_analysis,
            corpora,
            processed_root,
            iconicity_csv,
            generate_plots,
            report_start=False,
        )
        await _safe_progress(ctx, 1, 3, "Corpora checked")
        result = await _in_thread(
            ctx,
            "Running token analysis",
            tools.analyze_tokens,
            corpora,
            generate_plots,
            processed_root,
            output_dir,
            iconicity_csv,
            report_start=False,
        )
        await _safe_progress(ctx, 3, 3, "Token analysis finished")
        return result

    @server.tool(structured_output=False)
    async def analyze_types(
        corpora: Annotated[list[str], Field(min_length=1)],
        ctx: Context,
        categories: list[str] | None = None,
        generate_plots: bool = False,
        type_count_mode: str = DEFAULT_TYPE_COUNT_MODE,
        processed_root: str = "Corpora_modified",
        output_dir: str = DEFAULT_TYPES_OUTPUT_DIR,
        iconicity_csv: str = DEFAULT_ICONICITY_CSV,
    ) -> dict:
        """Run the grammatical types analysis for the named corpora.

        corpora must contain one or more names from list_corpora.
        type_count_mode is with_repetitions or only_once.
        """
        await _safe_progress(ctx, 0, 3, "Checking corpora")
        await _in_thread(
            ctx,
            "Checking corpora",
            tools.prepare_analysis,
            corpora,
            processed_root,
            iconicity_csv,
            generate_plots,
            categories,
            type_count_mode,
            report_start=False,
        )
        await _safe_progress(ctx, 1, 3, "Corpora checked")
        result = await _in_thread(
            ctx,
            "Running types analysis",
            tools.analyze_types,
            corpora,
            categories,
            generate_plots,
            type_count_mode,
            processed_root,
            output_dir,
            iconicity_csv,
            report_start=False,
        )
        await _safe_progress(ctx, 3, 3, "Types analysis finished")
        return result

    @server.tool(structured_output=False)
    async def export_rated(
        ctx: Context,
        source_dir: str = DEFAULT_TYPES_OUTPUT_DIR,
        output_dir: str = DEFAULT_RATED_OUTPUT_DIR,
        iconicity_csv: str = DEFAULT_ICONICITY_CSV,
    ) -> dict:
        """Add iconicity ratings to a types export. Run analyze_types first."""
        return await _in_thread(
            ctx,
            "Exporting rated categories",
            tools.export_rated,
            source_dir,
            output_dir,
            iconicity_csv,
        )

    @server.resource(
        "childconicity://results/{name}",
        mime_type="application/json",
        description="Full path map for one analysis summary.",
    )
    def result_resource(name: str) -> str:
        try:
            return tools.read_result(name)
        except ToolError as exc:
            raise ResourceNotFoundError(str(exc)) from exc

    @server.resource(
        "childconicity://corpora",
        mime_type="application/json",
        description="Normalized corpora currently available on disk.",
    )
    def corpora_resource() -> str:
        return tools.read_corpora_resource()

    @server.resource(
        "childconicity://citation",
        mime_type="text/yaml",
        description="Software citation for ChildConicity.",
    )
    def citation_resource() -> str:
        try:
            return tools.read_citation()
        except ToolError as exc:
            raise ResourceNotFoundError(str(exc)) from exc

    return server


async def _safe_progress(ctx: Context, progress: float, total: float, message: str) -> None:
    try:
        await ctx.report_progress(progress, total, message)
    except ValueError:
        return


def _report_from_thread(ctx: Context, progress: float, total: float, message: str) -> None:
    try:
        anyio.from_thread.run(_safe_progress, ctx, progress, total, message)
    except RuntimeError:
        return


async def _in_thread(ctx: Context, label: str, fn, *args, report_start: bool = True):
    if report_start:
        await _safe_progress(ctx, 0, 1, label)
    try:
        result = await anyio.to_thread.run_sync(lambda: fn(*args))
    except ToolError:
        raise
    if report_start:
        await _safe_progress(ctx, 1, 1, "Done")
    return result


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
