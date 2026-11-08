import inspect
import json

import pytest

from src.cli.download_corpora import TALKBANK_PASSWORD_ENV, TALKBANK_USER_ENV
from src.corpus_initialization.initializer import CorpusInitializer
from src.mcp_server.errors import ToolError
from src.mcp_server.tools import (
    NORMALIZE_STEPS,
    analyze_tokens,
    analyze_types,
    check_preconditions,
    download_corpora,
    download_iconicity_ratings,
    export_rated,
    list_categories,
    list_corpora,
    normalize_corpora,
    read_citation,
    read_result,
    summarize_result,
)


def _use_project(tmp_path, monkeypatch, *, ratings=True, corpora=("Brent",)):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv(TALKBANK_USER_ENV, raising=False)
    monkeypatch.delenv(TALKBANK_PASSWORD_ENV, raising=False)
    if ratings:
        ratings_path = tmp_path / "iconicity_ratings"
        ratings_path.mkdir()
        (ratings_path / "iconicity_ratings_cleaned.csv").write_text(
            "lemma,rating\n", encoding="utf-8"
        )
    processed = tmp_path / "Corpora_modified"
    processed.mkdir()
    for name in corpora:
        (processed / name).mkdir()
    return tmp_path


def test_check_preconditions_reports_flags_without_secrets(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)
    monkeypatch.setenv(TALKBANK_USER_ENV, "person@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "super-secret-value")
    (tmp_path / "quarterly_grammatical_categories").mkdir()
    (tmp_path / "quarterly_grammatical_categories" / "adults").mkdir()

    result = check_preconditions()

    assert result["ratings_present"] is True
    assert result["processed_root_present"] is True
    assert result["types_output_present"] is True
    assert result["talkbank_credentials_present"] is True
    assert "super-secret-value" not in json.dumps(result)


def test_check_preconditions_when_inputs_are_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv(TALKBANK_USER_ENV, raising=False)
    monkeypatch.delenv(TALKBANK_PASSWORD_ENV, raising=False)

    result = check_preconditions()

    assert result["ratings_present"] is False
    assert result["processed_root_present"] is False
    assert result["types_output_present"] is False
    assert result["talkbank_credentials_present"] is False


def test_list_corpora_and_categories(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch, corpora=("Brent", "Post"))

    assert list_corpora() == {"corpora": ["Brent", "Post"]}
    categories = list_categories()["categories"]
    assert "noun" in categories
    assert "verb" in categories


def test_list_corpora_rejects_a_root_with_the_wrong_name(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))

    with pytest.raises(ToolError, match="Corpora_modified"):
        list_corpora("Corpora")


def test_analyze_tokens_rejects_an_empty_selection(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    with pytest.raises(ToolError, match="at least one corpus"):
        analyze_tokens([])


def test_analyze_tokens_rejects_unknown_corpora(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch, corpora=("Brent",))

    with pytest.raises(ToolError, match="Unknown corpora: Missing") as exc_info:
        analyze_tokens(["Missing"])

    assert "Brent" in str(exc_info.value)


def test_analyze_tokens_requires_ratings(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch, ratings=False)

    with pytest.raises(ToolError, match="download_iconicity_ratings"):
        analyze_tokens(["Brent"])


def test_analyze_tokens_requires_processed_corpora(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    ratings = tmp_path / "iconicity_ratings"
    ratings.mkdir()
    (ratings / "iconicity_ratings_cleaned.csv").write_text("lemma\n", encoding="utf-8")

    with pytest.raises(ToolError, match="normalize_corpora"):
        analyze_tokens(["Brent"])


def test_analyze_tokens_summary_hides_service_stdout(tmp_path, monkeypatch, capsys):
    _use_project(tmp_path, monkeypatch)

    def noisy(*args, **kwargs):
        print("TOKEN-STDOUT")
        return {
            "outputs": {"adults": {"json": str(tmp_path / "a.json")}},
            "plot_outputs": {"files": {"by_age": str(tmp_path / "plot.png")}},
        }

    monkeypatch.setattr("src.mcp_server.tools.run_tokens_analysis", noisy)

    summary = analyze_tokens(["brent"])

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "TOKEN-STDOUT" in captured.err
    assert summary["mode"] == "tokens"
    assert summary["files_written"] == 1
    assert summary["plot_files"] == 1
    assert summary["sample_paths"] == ["a.json", "plot.png"]
    saved = (tmp_path / summary["result_file"]).read_text(encoding="utf-8")
    assert "a.json" in saved


def test_analyze_types_rejects_unknown_categories(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    with pytest.raises(ToolError, match="Unknown categories: particle"):
        analyze_types(["Brent"], categories=["particle"])


def test_analyze_types_rejects_unknown_count_mode(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    with pytest.raises(ToolError, match="type_count_mode"):
        analyze_types(["Brent"], type_count_mode="twice")


def test_summarize_result_limits_sample_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    outputs = {f"file-{index}": f"path-{index}.json" for index in range(12)}

    summary = summarize_result(
        "types",
        {"outputs": outputs, "plot_outputs": None},
        "quarterly_grammatical_categories",
    )

    assert summary["files_written"] == 12
    assert len(summary["sample_paths"]) == 10
    assert summary["plot_files"] == 0
    stored = json.loads((tmp_path / summary["result_file"]).read_text(encoding="utf-8"))
    assert stored["outputs"]["file-0"] == "path-0.json"


def test_export_rated_requires_types_output(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    with pytest.raises(ToolError, match="analyze_types first"):
        export_rated()


def test_export_rated_writes_a_summary(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)
    source = tmp_path / "quarterly_grammatical_categories" / "adults"
    source.mkdir(parents=True)
    (source / "0.json").write_text("{}", encoding="utf-8")

    def fake_export(**kwargs):
        print("RATED-STDOUT")
        return {"outputs": {"source_dir": kwargs["source_dir"], "output_dir": kwargs["output_dir"]}}

    monkeypatch.setattr("src.mcp_server.tools.run_rated_export", fake_export)

    summary = export_rated()

    assert summary["mode"] == "rated"
    assert summary["files_written"] == 2
    assert len(summary["sample_paths"]) == 2


def test_download_iconicity_ratings_reports_skip(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    result = download_iconicity_ratings()

    assert result["downloaded"] is False
    assert result["path"] == "iconicity_ratings/iconicity_ratings_cleaned.csv"


def test_download_iconicity_ratings_hides_network_detail(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch, ratings=False)
    requests = pytest.importorskip("requests")

    def fail(**kwargs):
        raise requests.ConnectionError("super-secret-value")

    monkeypatch.setattr("src.mcp_server.tools.download_ratings_file", fail)

    with pytest.raises(ToolError, match="ConnectionError") as exc_info:
        download_iconicity_ratings()

    assert "super-secret-value" not in str(exc_info.value)


def test_download_corpora_has_no_password_parameter():
    assert "password" not in inspect.signature(download_corpora).parameters
    assert "user" not in inspect.signature(download_corpora).parameters


def test_download_corpora_requires_environment_credentials(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    with pytest.raises(ToolError, match=TALKBANK_PASSWORD_ENV) as exc_info:
        download_corpora(["Brent"])

    assert "argument" in str(exc_info.value)


def test_download_corpora_login_failure_omits_the_secret(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)
    monkeypatch.setenv(TALKBANK_USER_ENV, "person@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "super-secret-value")

    def fake_run(*args, **kwargs):
        assert args[1] == "super-secret-value"
        assert kwargs["headless"] is True
        assert "on_corpus" not in kwargs
        print("ERROR: Authentication error: rejected")

    monkeypatch.setattr("src.mcp_server.tools.run_download", fake_run)

    with pytest.raises(ToolError, match=TALKBANK_PASSWORD_ENV) as exc_info:
        download_corpora(["Brent"])

    assert "super-secret-value" not in str(exc_info.value)


def test_download_corpora_browser_errors_are_short(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)
    monkeypatch.setenv(TALKBANK_USER_ENV, "person@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "super-secret-value")
    from selenium.common.exceptions import WebDriverException

    def fake_run(*args, **kwargs):
        raise WebDriverException("super-secret-value")

    monkeypatch.setattr("src.mcp_server.tools.run_download", fake_run)

    with pytest.raises(ToolError, match="Check Chrome") as exc_info:
        download_corpora(["Brent"])

    assert "super-secret-value" not in str(exc_info.value)


def test_normalize_steps_exist_on_the_initializer():
    for _name, method_name in NORMALIZE_STEPS:
        assert hasattr(CorpusInitializer, method_name)


def test_normalize_corpora_reports_each_corpus(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    (tmp_path / "Corpora").mkdir()
    seen = []

    class FakeInitializer:
        def __init__(self, source_root, output_root):
            self.source_root = source_root
            self.output_root = output_root

        def initialize_bates(self):
            print("NORMALIZE-STDOUT")
            seen.append(self.source_root)

        def initialize_brent(self):
            seen.append(self.output_root)

    monkeypatch.setattr(
        "src.mcp_server.tools.NORMALIZE_STEPS",
        (("Bates", "initialize_bates"), ("Brent", "initialize_brent")),
    )
    monkeypatch.setattr("src.mcp_server.tools.CorpusInitializer", FakeInitializer)

    result = normalize_corpora()

    assert result["corpora"] == ["Bates", "Brent"]
    assert result["output_root"] == "Corpora_modified"
    assert len(seen) == 2


def test_normalize_corpora_requires_the_source_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))

    with pytest.raises(ToolError, match="download_corpora"):
        normalize_corpora()


def test_normalize_corpora_hides_internal_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    (tmp_path / "Corpora" / "Bates").mkdir(parents=True)

    class FakeInitializer:
        def __init__(self, source_root, output_root):
            pass

        def initialize_bates(self):
            raise RuntimeError("super-secret-value")

    monkeypatch.setattr(
        "src.mcp_server.tools.NORMALIZE_STEPS",
        (("Bates", "initialize_bates"),),
    )
    monkeypatch.setattr("src.mcp_server.tools.CorpusInitializer", FakeInitializer)

    with pytest.raises(ToolError, match="Could not normalize Bates") as exc_info:
        normalize_corpora()

    assert "super-secret-value" not in str(exc_info.value)
    assert "RuntimeError" in str(exc_info.value)


def test_read_result_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    secret = tmp_path / "secret.txt"
    secret.write_text("super-secret-value", encoding="utf-8")

    with pytest.raises(ToolError, match="Invalid result name"):
        read_result("../secret.txt")

    with pytest.raises(ToolError, match="Invalid result name"):
        read_result("nested/file.json")


def test_read_result_returns_a_stored_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    folder = tmp_path / ".childconicity_mcp"
    folder.mkdir()
    (folder / "types_test.json").write_text('{"outputs": {}}\n', encoding="utf-8")

    assert '"outputs"' in read_result("types_test.json")


def test_read_citation_uses_the_project_root(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))

    with pytest.raises(ToolError, match="CITATION.cff"):
        read_citation()

    (tmp_path / "CITATION.cff").write_text("title: Test\n", encoding="utf-8")
    assert read_citation() == "title: Test\n"


def test_project_root_defaults_to_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("CHILDCONICITY_PROJECT_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)

    from src.mcp_server.tools import project_root

    assert project_root() == tmp_path.resolve()


def test_summary_keeps_an_output_dir_outside_the_project(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))

    summary = summarize_result(
        "tokens",
        {"outputs": {"rows": ["one", "two"]}, "plot_outputs": None},
        "/outside/project/out",
    )

    assert summary["output_dir"] == "/outside/project/out"
    assert summary["sample_paths"] == ["one", "two"]


def test_processed_root_must_use_the_canonical_name(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))

    with pytest.raises(ToolError, match="must be named Corpora_modified"):
        analyze_tokens(["Brent"], processed_root="Corpora")


def test_plots_require_the_plot_libraries(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)
    monkeypatch.setattr("src.mcp_server.tools._plots_available", lambda: False)

    with pytest.raises(ToolError, match="matplotlib"):
        analyze_tokens(["Brent"], generate_plots=True)


def test_analyze_types_summarizes_the_export(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    def fake_types(*args, **kwargs):
        assert kwargs["categories"] == ["noun"]
        assert kwargs["type_count_mode"] == "only_once"
        return {"outputs": {"json": "types.json"}, "plot_outputs": None}

    monkeypatch.setattr("src.mcp_server.tools.run_types_analysis", fake_types)

    summary = analyze_types(["Brent"], categories=["noun"], type_count_mode="only_once")

    assert summary["mode"] == "types"
    assert summary["sample_paths"] == ["types.json"]


def test_token_analysis_turns_value_errors_into_tool_errors(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    def fail(*args, **kwargs):
        raise ValueError("Processed root must be named 'Corpora_modified'.")

    monkeypatch.setattr("src.mcp_server.tools.run_tokens_analysis", fail)

    with pytest.raises(ToolError, match="Corpora_modified"):
        analyze_tokens(["Brent"])


def test_download_corpora_rejects_an_empty_selection(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)

    with pytest.raises(ToolError, match="at least one corpus"):
        download_corpora([])


def test_download_corpora_reports_permission_and_total_failure(tmp_path, monkeypatch):
    _use_project(tmp_path, monkeypatch)
    monkeypatch.setenv(TALKBANK_USER_ENV, "person@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "super-secret-value")

    def deny(*args, **kwargs):
        raise PermissionError("rejected")

    monkeypatch.setattr("src.mcp_server.tools.run_download", deny)
    with pytest.raises(ToolError, match="login was rejected") as exc_info:
        download_corpora(["Brent"])
    assert "super-secret-value" not in str(exc_info.value)

    def failed(*args, **kwargs):
        print("Summary: 0 downloaded, 0 skipped, 1 failed.")

    monkeypatch.setattr("src.mcp_server.tools.run_download", failed)
    with pytest.raises(ToolError, match="failed for 1"):
        download_corpora(["Brent"])


def test_normalize_invokes_the_progress_callback(tmp_path, monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    (tmp_path / "Corpora").mkdir()
    seen = []

    class FakeInitializer:
        def __init__(self, source_root, output_root):
            pass

        def initialize_bates(self):
            return None

    monkeypatch.setattr(
        "src.mcp_server.tools.NORMALIZE_STEPS",
        (("Bates", "initialize_bates"),),
    )
    monkeypatch.setattr("src.mcp_server.tools.CorpusInitializer", FakeInitializer)

    result = normalize_corpora(on_corpus=lambda name, index, total: seen.append(name))

    assert result["corpora"] == ["Bates"]
    assert seen == ["Bates"]


def test_server_registers_the_pipeline_tools():
    pytest.importorskip("mcp")
    import anyio

    from src.mcp_server.server import build_server

    server = build_server()
    listed = anyio.run(server.list_tools)
    assert [tool.name for tool in listed] == [
        "check_preconditions",
        "list_corpora",
        "list_categories",
        "download_iconicity_ratings",
        "download_corpora",
        "normalize_corpora",
        "analyze_tokens",
        "analyze_types",
        "export_rated",
    ]
    download = next(tool for tool in listed if tool.name == "download_corpora")
    properties = download.input_schema["properties"]
    assert "password" not in properties
    assert "user" not in properties
    assert "corpora" in download.input_schema["required"]


def test_server_analyze_tokens_returns_summary(tmp_path, monkeypatch):
    pytest.importorskip("mcp")
    import anyio

    from mcp.server.mcpserver.exceptions import ToolError as ProtocolToolError

    from src.mcp_server.server import build_server

    _use_project(tmp_path, monkeypatch)

    def fake_analysis(*args, **kwargs):
        print("SERVER-STDOUT")
        return {"outputs": {"json": "tokens.json"}, "plot_outputs": None}

    monkeypatch.setattr("src.mcp_server.tools.run_tokens_analysis", fake_analysis)
    server = build_server()

    with pytest.raises(ProtocolToolError):
        anyio.run(server.call_tool, "analyze_tokens", {"corpora": []})

    result = anyio.run(
        server.call_tool, "analyze_tokens", {"corpora": ["Brent"]}
    )

    assert result.is_error is False
    assert "tokens.json" in result.content[0].text


def test_server_resources_and_traversal(tmp_path, monkeypatch):
    pytest.importorskip("mcp")
    import anyio

    from mcp.server.mcpserver.exceptions import ResourceNotFoundError

    from src.mcp_server.server import build_server

    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(tmp_path))
    (tmp_path / "Corpora_modified" / "Brent").mkdir(parents=True)
    (tmp_path / "CITATION.cff").write_text("title: Test\n", encoding="utf-8")
    folder = tmp_path / ".childconicity_mcp"
    folder.mkdir()
    (folder / "types_test.json").write_text('{"ok": true}\n', encoding="utf-8")
    server = build_server()

    citation = anyio.run(server.read_resource, "childconicity://citation")
    corpora = anyio.run(server.read_resource, "childconicity://corpora")
    stored = anyio.run(server.read_resource, "childconicity://results/types_test.json")

    assert "title: Test" in citation[0].content
    assert "Brent" in corpora[0].content
    assert '"ok": true' in stored[0].content

    with pytest.raises(Exception):
        anyio.run(server.read_resource, "childconicity://results/../CITATION.cff")

    with pytest.raises(ResourceNotFoundError):
        anyio.run(server.read_resource, "childconicity://results/missing.json")

    empty = tmp_path / "empty-project"
    empty.mkdir()
    monkeypatch.setenv("CHILDCONICITY_PROJECT_ROOT", str(empty))
    with pytest.raises(ResourceNotFoundError, match="CITATION.cff"):
        anyio.run(server.read_resource, "childconicity://citation")


def test_server_runs_the_remaining_tools(tmp_path, monkeypatch, capsys):
    pytest.importorskip("mcp")
    import anyio

    from mcp.server.mcpserver.exceptions import ToolError as ProtocolToolError

    from src.mcp_server.server import build_server

    _use_project(tmp_path, monkeypatch)
    (tmp_path / "Corpora").mkdir()
    types_dir = tmp_path / "quarterly_grammatical_categories" / "adults"
    types_dir.mkdir(parents=True)
    (types_dir / "0.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv(TALKBANK_USER_ENV, "person@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "super-secret-value")

    def fake_download(*args, **kwargs):
        print("Summary: 1 downloaded, 0 skipped, 0 failed.")

    class FakeInitializer:
        def __init__(self, source_root, output_root):
            pass

        def initialize_bates(self):
            return None

    def fake_types(*args, **kwargs):
        return {"outputs": {"json": "types.json"}, "plot_outputs": None}

    def fake_rated(**kwargs):
        return {"outputs": {"output_dir": kwargs["output_dir"]}}

    monkeypatch.setattr("src.mcp_server.tools.run_download", fake_download)
    monkeypatch.setattr(
        "src.mcp_server.tools.NORMALIZE_STEPS",
        (("Bates", "initialize_bates"),),
    )
    monkeypatch.setattr("src.mcp_server.tools.CorpusInitializer", FakeInitializer)
    monkeypatch.setattr("src.mcp_server.tools.run_types_analysis", fake_types)
    monkeypatch.setattr("src.mcp_server.tools.run_rated_export", fake_rated)
    server = build_server()

    preconditions = anyio.run(server.call_tool, "check_preconditions", {})
    listed = anyio.run(server.call_tool, "list_corpora", {})
    categories = anyio.run(server.call_tool, "list_categories", {})
    ratings = anyio.run(
        server.call_tool, "download_iconicity_ratings", {"force": False}
    )
    downloaded = anyio.run(
        server.call_tool, "download_corpora", {"corpora": ["Brent"]}
    )
    normalized = anyio.run(server.call_tool, "normalize_corpora", {})
    types = anyio.run(
        server.call_tool, "analyze_types", {"corpora": ["Brent"]}
    )
    rated = anyio.run(server.call_tool, "export_rated", {})

    assert preconditions.is_error is False
    assert "Brent" in listed.content[0].text
    assert "noun" in categories.content[0].text
    assert "downloaded" in ratings.content[0].text
    assert "super-secret-value" not in downloaded.content[0].text
    assert "Bates" in normalized.content[0].text
    assert "types.json" in types.content[0].text
    assert rated.is_error is False
    captured = capsys.readouterr()
    assert "super-secret-value" not in captured.out

    with pytest.raises(ProtocolToolError, match="Corpora_modified"):
        anyio.run(server.call_tool, "list_corpora", {"processed_root": "Corpora"})
