"""Pure functions behind the ChildConicity MCP tools.

Service code prints progress to stdout. While these functions run, that
stream is sent to stderr so it cannot corrupt the stdio MCP channel.
"""

import contextlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from selenium.common.exceptions import WebDriverException

from src.analysis.grammatical_type_analysis import TYPE_COUNT_MODES
from src.cli.download_corpora import (
    DEFAULT_OUTPUT_DIR,
    TALKBANK_PASSWORD_ENV,
    TALKBANK_USER_ENV,
    resolve_talkbank_credentials,
    run as run_download,
)
from src.cli.download_iconicity_ratings import (
    download_iconicity_ratings as download_ratings_file,
)
from src.corpus_initialization.initializer import CorpusInitializer
from src.gui.services import (
    DEFAULT_ICONICITY_CSV,
    DEFAULT_RATED_OUTPUT_DIR,
    DEFAULT_TOKENS_OUTPUT_DIR,
    DEFAULT_TYPE_COUNT_MODE,
    DEFAULT_TYPES_OUTPUT_DIR,
    get_available_categories,
    get_available_corpora,
    run_rated_export,
    run_tokens_analysis,
    run_types_analysis,
)
from src.mcp_server.errors import ToolError

RESULTS_DIR_NAME = ".childconicity_mcp"
PROJECT_ROOT_ENV = "CHILDCONICITY_PROJECT_ROOT"
SAMPLE_PATH_LIMIT = 10

NORMALIZE_STEPS = (
    ("Bates", "initialize_bates"),
    ("Brent", "initialize_brent"),
    ("NewEngland", "initialize_new_england"),
    ("Post", "initialize_post"),
    ("Bloom", "initialize_bloom"),
    ("Brown", "initialize_brown"),
    ("HSLLD", "initialize_hslld"),
    ("Kuczaj", "initialize_kuczaj"),
    ("Sachs", "initialize_sachs"),
    ("VanKleeck", "initialize_van_kleeck"),
    ("Providence", "initialize_providence"),
)

_PLOT_MODULES = ("matplotlib", "numpy", "seaborn")
_DOWNLOAD_FAILURE = (
    "TalkBank download failed. Check Chrome and the network, then retry."
)
_LOGIN_FAILURE = (
    "TalkBank login was rejected. Check "
    f"{TALKBANK_USER_ENV} and {TALKBANK_PASSWORD_ENV}."
)


@contextlib.contextmanager
def _quiet_stdout():
    with contextlib.redirect_stdout(sys.stderr):
        yield


def project_root() -> Path:
    raw = os.environ.get(PROJECT_ROOT_ENV)
    if raw:
        return Path(raw).expanduser().resolve()
    return Path.cwd().resolve()


def resolve_path(path: str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = project_root() / candidate
    return candidate.resolve()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root()).as_posix()
    except ValueError:
        return str(resolved)


def results_dir(*, create: bool = False) -> Path:
    path = project_root() / RESULTS_DIR_NAME
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def _plots_available() -> bool:
    return all(importlib.util.find_spec(name) is not None for name in _PLOT_MODULES)


def _credentials_present() -> bool:
    return bool(os.environ.get(TALKBANK_USER_ENV)) and bool(
        os.environ.get(TALKBANK_PASSWORD_ENV)
    )


def _require_ratings(path: Path) -> None:
    if not path.is_file():
        raise ToolError(
            "Iconicity ratings are missing "
            f"({display_path(path)}). Run download_iconicity_ratings."
        )


def _require_processed(path: Path) -> None:
    if path.name != "Corpora_modified":
        raise ToolError("Processed root must be named Corpora_modified.")
    if not path.is_dir():
        raise ToolError(
            "Processed corpora are missing "
            f"({display_path(path)}). Run normalize_corpora."
        )


def _require_types_output(path: Path) -> None:
    if not path.is_dir() or not any(path.iterdir()):
        raise ToolError(
            "Types output is missing "
            f"({display_path(path)}). Run analyze_types first."
        )


def _canonical_corpora(corpora, processed: Path) -> list[str]:
    if not corpora:
        raise ToolError(
            "Select at least one corpus. Call list_corpora to see the names "
            "available under Corpora_modified."
        )
    available = get_available_corpora(str(processed))
    known = {name.casefold(): name for name in available}
    unknown = [name for name in corpora if name.casefold() not in known]
    if unknown:
        valid = ", ".join(available) if available else "(none)"
        raise ToolError(
            f"Unknown corpora: {', '.join(unknown)}. Valid corpora: {valid}."
        )
    return [known[name.casefold()] for name in corpora]


def _canonical_categories(categories) -> list[str] | None:
    if not categories:
        return None
    available = list(get_available_categories(""))
    known = {name.casefold(): name for name in available}
    unknown = [name for name in categories if name.casefold() not in known]
    if unknown:
        raise ToolError(
            f"Unknown categories: {', '.join(unknown)}. "
            f"Valid categories: {', '.join(available)}."
        )
    return [known[name.casefold()] for name in categories]


def _check_type_count_mode(type_count_mode: str) -> str:
    if type_count_mode not in TYPE_COUNT_MODES:
        valid = ", ".join(TYPE_COUNT_MODES)
        raise ToolError(
            f"Unknown type_count_mode: {type_count_mode}. Valid modes: {valid}."
        )
    return type_count_mode


def _require_plots(generate_plots: bool) -> None:
    if generate_plots and not _plots_available():
        raise ToolError(
            "Plot libraries are missing. Install matplotlib, numpy, and seaborn."
        )


def _string_leaves(value):
    found = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(_string_leaves(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_string_leaves(item))
    return found


def _display_leaf(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return display_path(path)
    return value


def summarize_result(mode: str, result: dict, output_dir: str) -> dict:
    """Write the runner path map and return a short summary."""
    payload = {
        "outputs": result.get("outputs"),
        "plot_outputs": result.get("plot_outputs"),
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    result_path = results_dir(create=True) / f"{mode}_{stamp}.json"
    result_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    output_paths = _string_leaves(payload.get("outputs"))
    plot_outputs = payload.get("plot_outputs") or {}
    plot_files = []
    if isinstance(plot_outputs, dict):
        plot_files = _string_leaves(plot_outputs.get("files"))
    sample = [_display_leaf(path) for path in (output_paths + plot_files)]
    output_path = Path(output_dir)
    shown_output = (
        display_path(output_path) if output_path.is_absolute() else output_dir
    )
    return {
        "mode": mode,
        "result_file": display_path(result_path),
        "output_dir": shown_output,
        "files_written": len(output_paths),
        "plot_files": len(plot_files),
        "sample_paths": sample[:SAMPLE_PATH_LIMIT],
    }


def check_preconditions(
    processed_root: str = "Corpora_modified",
    types_output: str = DEFAULT_TYPES_OUTPUT_DIR,
    iconicity_csv: str = DEFAULT_ICONICITY_CSV,
) -> dict:
    """Report whether local inputs are present. Never returns secret values."""
    ratings = resolve_path(iconicity_csv)
    processed = resolve_path(processed_root)
    types_dir = resolve_path(types_output)
    types_ready = types_dir.is_dir() and any(types_dir.iterdir())
    return {
        "ratings_present": ratings.is_file(),
        "processed_root_present": processed.is_dir(),
        "types_output_present": types_ready,
        "plots_available": _plots_available(),
        "talkbank_credentials_present": _credentials_present(),
    }


def list_corpora(processed_root: str = "Corpora_modified") -> dict:
    """List corpus directories under the processed root."""
    path = resolve_path(processed_root)
    if path.name != "Corpora_modified":
        raise ToolError("Processed root must be named Corpora_modified.")
    return {"corpora": get_available_corpora(str(path))}


def list_categories(processed_root: str = "Corpora_modified") -> dict:
    """List the grammatical categories the types analysis accepts."""
    return {
        "categories": list(get_available_categories(str(resolve_path(processed_root))))
    }


def download_iconicity_ratings(force: bool = False) -> dict:
    """Download the iconicity ratings CSV if it is not already present."""
    path = resolve_path(DEFAULT_ICONICITY_CSV)
    try:
        with _quiet_stdout():
            downloaded = download_ratings_file(output_path=path, force=force)
    except requests.RequestException as exc:
        raise ToolError(
            "Iconicity ratings download failed: "
            f"{type(exc).__name__}. Retry later."
        ) from exc
    return {"path": display_path(path), "downloaded": bool(downloaded)}


def download_corpora(corpora: list[str], force: bool = False, on_corpus=None) -> dict:
    """Download TalkBank corpora with headless Chrome.

    Credentials come from the environment. This function has no user or
    password parameter.
    """
    if not corpora:
        raise ToolError("Select at least one corpus to download.")
    try:
        email, password = resolve_talkbank_credentials(None, None)
    except ValueError as exc:
        raise ToolError(
            "TalkBank credentials are missing. Set "
            f"{TALKBANK_USER_ENV} and {TALKBANK_PASSWORD_ENV} in the environment. "
            "Do not pass the password as an argument."
        ) from exc

    output_dir = resolve_path(DEFAULT_OUTPUT_DIR)
    try:
        with _quiet_stdout():
            summary = run_download(
                email,
                password,
                corpora,
                str(output_dir),
                force,
                headless=True,
                on_corpus=on_corpus,
            )
    except PermissionError as exc:
        raise ToolError(_LOGIN_FAILURE) from exc
    except (requests.RequestException, WebDriverException, OSError) as exc:
        raise ToolError(_DOWNLOAD_FAILURE) from exc

    if not summary or summary.get("error"):
        raise ToolError(_LOGIN_FAILURE)
    if summary["failed"] and not summary["downloaded"] and not summary["skipped"]:
        raise ToolError(
            f"TalkBank download failed for {summary['failed']} corpora. "
            "Check Chrome, the network, and the corpus names, then retry."
        )
    return {
        "output_dir": display_path(output_dir),
        "requested": list(summary["requested"]),
        "downloaded": summary["downloaded"],
        "skipped": summary["skipped"],
        "failed": summary["failed"],
    }


def normalize_corpora(
    source_root: str = "Corpora",
    output_root: str = "Corpora_modified",
    on_corpus=None,
) -> dict:
    """Normalize downloaded corpora into Corpora_modified."""
    source = resolve_path(source_root)
    output = resolve_path(output_root)
    if not source.is_dir():
        raise ToolError(
            f"Source corpora are missing ({display_path(source)}). "
            "Run download_corpora."
        )
    initializer = CorpusInitializer(str(source), str(output))
    done = []
    total = len(NORMALIZE_STEPS)
    with _quiet_stdout():
        for index, (name, method_name) in enumerate(NORMALIZE_STEPS, start=1):
            if on_corpus is not None:
                on_corpus(name, index, total)
            try:
                getattr(initializer, method_name)()
            except ToolError:
                raise
            except Exception as exc:
                raise ToolError(
                    f"Could not normalize {name}: {type(exc).__name__}. "
                    f"Check that {display_path(source / name)} exists."
                ) from exc
            done.append(name)
    return {"output_root": display_path(output), "corpora": done}


def prepare_analysis(
    corpora,
    processed_root: str,
    iconicity_csv: str,
    generate_plots: bool,
    categories=None,
    type_count_mode: str | None = None,
):
    processed = resolve_path(processed_root)
    ratings = resolve_path(iconicity_csv)
    _require_processed(processed)
    _require_ratings(ratings)
    _require_plots(generate_plots)
    selected = _canonical_corpora(corpora, processed)
    selected_categories = _canonical_categories(categories)
    if type_count_mode is not None:
        type_count_mode = _check_type_count_mode(type_count_mode)
    return processed, ratings, selected, selected_categories, type_count_mode


def analyze_tokens(
    corpora: list[str],
    generate_plots: bool = False,
    processed_root: str = "Corpora_modified",
    output_dir: str = DEFAULT_TOKENS_OUTPUT_DIR,
    iconicity_csv: str = DEFAULT_ICONICITY_CSV,
) -> dict:
    """Run the token analysis for an explicit corpus list."""
    processed, ratings, selected, _, _ = prepare_analysis(
        corpora,
        processed_root,
        iconicity_csv,
        generate_plots,
    )
    destination = resolve_path(output_dir)
    try:
        with _quiet_stdout():
            result = run_tokens_analysis(
                str(processed),
                selected_corpora=selected,
                output_dir=str(destination),
                iconicity_csv=str(ratings),
                generate_plots=generate_plots,
            )
    except ToolError:
        raise
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return summarize_result("tokens", result, display_path(destination))


def analyze_types(
    corpora: list[str],
    categories: list[str] | None = None,
    generate_plots: bool = False,
    type_count_mode: str = DEFAULT_TYPE_COUNT_MODE,
    processed_root: str = "Corpora_modified",
    output_dir: str = DEFAULT_TYPES_OUTPUT_DIR,
    iconicity_csv: str = DEFAULT_ICONICITY_CSV,
) -> dict:
    """Run the grammatical types analysis for an explicit corpus list."""
    processed, ratings, selected, selected_categories, selected_mode = (
        prepare_analysis(
            corpora,
            processed_root,
            iconicity_csv,
            generate_plots,
            categories=categories,
            type_count_mode=type_count_mode,
        )
    )
    destination = resolve_path(output_dir)
    try:
        with _quiet_stdout():
            result = run_types_analysis(
                str(processed),
                selected_corpora=selected,
                categories=selected_categories,
                output_dir=str(destination),
                iconicity_csv=str(ratings),
                generate_plots=generate_plots,
                type_count_mode=selected_mode,
            )
    except ToolError:
        raise
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    return summarize_result("types", result, display_path(destination))


def export_rated(
    source_dir: str = DEFAULT_TYPES_OUTPUT_DIR,
    output_dir: str = DEFAULT_RATED_OUTPUT_DIR,
    iconicity_csv: str = DEFAULT_ICONICITY_CSV,
) -> dict:
    """Attach iconicity ratings to a previous types export."""
    source = resolve_path(source_dir)
    ratings = resolve_path(iconicity_csv)
    destination = resolve_path(output_dir)
    _require_types_output(source)
    _require_ratings(ratings)
    with _quiet_stdout():
        result = run_rated_export(
            source_dir=str(source),
            output_dir=str(destination),
            iconicity_csv=str(ratings),
        )
    return summarize_result("rated", result, display_path(destination))


def _valid_result_name(name: str) -> bool:
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        return False
    return ".." not in Path(name).parts and name == Path(name).name


def read_result(name: str) -> str:
    """Return one stored analysis summary."""
    if not _valid_result_name(name):
        raise ToolError("Invalid result name.")
    path = (results_dir() / name).resolve()
    root = results_dir().resolve()
    if path.parent != root:
        raise ToolError("Invalid result name.")
    if not path.is_file():
        raise ToolError(f"Result not found: {name}")
    return path.read_text(encoding="utf-8")


def read_corpora_resource() -> str:
    return json.dumps(list_corpora(), ensure_ascii=False)


def read_citation() -> str:
    path = project_root() / "CITATION.cff"
    if not path.is_file():
        raise ToolError("CITATION.cff was not found in the project root.")
    return path.read_text(encoding="utf-8")
