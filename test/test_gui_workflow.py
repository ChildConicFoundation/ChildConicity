"""Manual GUI workflows.

These tests open the real Tkinter window and operate the controls a person
uses. The corpus pipeline and the external analysis process are replaced so
the test checks the window, the validation, and the command the GUI builds.
"""

import importlib.util
from pathlib import Path

import pytest

tk = pytest.importorskip("tkinter")

from src.gui.app import ChildConicityApp, _project_root
from src.gui.services import (
    DEFAULT_TOKENS_OUTPUT_DIR,
    DEFAULT_TYPES_OUTPUT_DIR,
    TYPE_COUNT_ONLY_ONCE,
)
from src.i18n import get_locale, set_locale, t

_GUI_TESTER_PATH = Path(__file__).with_name("gui_tester.py")
_gui_tester_spec = importlib.util.spec_from_file_location(
    "childconicity_gui_tester",
    _GUI_TESTER_PATH,
)
_gui_tester = importlib.util.module_from_spec(_gui_tester_spec)
_gui_tester_spec.loader.exec_module(_gui_tester)

AnalysisProcessDouble = _gui_tester.AnalysisProcessDouble
DialogLog = _gui_tester.DialogLog
DirectoryChooser = _gui_tester.DirectoryChooser
GuiTester = _gui_tester.GuiTester


pytestmark = pytest.mark.gui


class _RecordingInitializer:
    def __init__(self, source_root, output_root):
        self.source_root = source_root
        self.output_root = output_root

    def initialize_all(self):
        for name in ("Brent", "Post"):
            Path(self.output_root, name).mkdir(parents=True, exist_ok=True)
        print("initialized corpora")


@pytest.fixture
def gui(monkeypatch, tmp_path):
    previous_locale = get_locale()
    set_locale("en")
    saved_locales = []
    monkeypatch.setattr("src.gui.app.save_locale", saved_locales.append)

    dialogs = DialogLog()
    monkeypatch.setattr("src.gui.app.messagebox.showerror", dialogs.showerror)
    monkeypatch.setattr("src.gui.app.messagebox.showinfo", dialogs.showinfo)
    monkeypatch.setattr("src.gui.app.messagebox.showwarning", dialogs.showwarning)

    directories = DirectoryChooser()
    monkeypatch.setattr(
        "src.gui.app.filedialog.askdirectory",
        directories.askdirectory,
    )

    analysis = AnalysisProcessDouble()
    monkeypatch.setattr("src.gui.app.subprocess.Popen", analysis)

    try:
        app = ChildConicityApp()
    except tk.TclError as exc:
        set_locale(previous_locale)
        pytest.skip(f"GUI workflow tests need a display: {exc}")

    app.withdraw()
    app.source_root.set(str(tmp_path / "missing" / "Corpora"))
    app.processed_root.set(str(tmp_path / "missing" / "Corpora_modified"))
    app.rated_source_dir.set(str(tmp_path / "missing" / "quarterly"))
    tester = GuiTester(app, dialogs, directories, analysis)
    tester.saved_locales = saved_locales
    tester.pump()

    yield tester

    analysis.release.set()
    try:
        app._handle_close()
    except tk.TclError:
        pass
    set_locale(previous_locale)


def test_app_opens_ready_for_a_manual_session(gui):
    assert gui.app.title() == "ChildConicity"
    assert gui.status() == t("gui.status.ready")
    assert gui.visible(t("gui.section.downloads"))
    assert gui.visible(t("gui.section.paths"))
    assert gui.visible(t("gui.section.corpus"))
    assert gui.visible(t("gui.section.analysis_mode"))
    assert gui.visible(t("gui.section.rated"))
    assert gui.visible(t("gui.section.log"))
    assert not gui.visible(t("gui.section.grammatical_categories"))
    assert not gui.visible(t("gui.section.type_count"))
    assert gui.visible(t("gui.empty.processed_not_found"))
    assert gui.is_enabled(t("gui.button.run_analysis"))
    assert not gui.is_enabled(t("gui.button.run_export"))
    assert gui.dialogs.entries == []


def test_language_switch_rewrites_the_visible_window(gui):
    gui.choose("Español")

    assert gui.saved_locales == ["es"]
    assert gui.status() == t("gui.status.ready")
    assert gui.visible(t("gui.section.downloads"))
    assert gui.visible(t("gui.button.run_analysis"))
    assert gui.visible(t("gui.button.initialize_corpora"))
    assert not gui.visible("Downloads")
    assert not gui.visible("Run analysis")

    gui.choose("English")

    assert gui.saved_locales == ["es", "en"]
    assert gui.visible("Run analysis")
    assert gui.status() == "Ready."
    assert not gui.visible("Ejecutar análisis")


def test_manual_mistakes_show_dialogs(gui, tmp_path):
    gui.tap(t("gui.button.download_corpora"))
    gui.expect_dialog(
        "error",
        t("gui.error.title"),
        t("gui.error.talkbank_credentials"),
    )

    source = tmp_path / "Corpora"
    processed = tmp_path / "Corpora_modified"
    gui.clear_dialogs()
    gui.enter(gui.app.source_root, str(source))
    gui.enter(gui.app.processed_root, str(processed))
    gui.tap(t("gui.button.initialize_corpora"))
    gui.expect_dialog(
        "error",
        t("gui.error.init_corpus"),
        t("gui.validation.source_missing", path=str(source)),
    )

    source.mkdir()
    gui.clear_dialogs()
    gui.enter(gui.app.processed_root, str(tmp_path / "Corpor_modified"))
    gui.tap(t("gui.button.initialize_corpora"))
    gui.expect_dialog(
        "error",
        t("gui.error.init_corpus"),
        t("gui.validation.processed_name", name="Corpora_modified"),
    )

    processed.mkdir()
    gui.clear_dialogs()
    gui.enter(gui.app.processed_root, str(processed))
    gui.tap(t("gui.button.run_analysis"))
    gui.expect_dialog(
        "error",
        t("gui.error.title"),
        t("gui.validation.no_corpora", path=str(processed)),
    )

    (processed / "Brent").mkdir()
    gui.clear_dialogs()
    gui.tap(t("gui.button.show_initialized"))
    gui.tap("Types")
    gui.tap(t("gui.checkbox.all_categories"))
    gui.tap(t("gui.button.run_analysis"))
    gui.expect_dialog(
        "error",
        t("gui.error.title"),
        t("gui.error.select_category"),
    )
    assert gui.analysis.commands == []


def test_initialize_then_run_tokens_for_one_corpus(gui, monkeypatch, tmp_path):
    monkeypatch.setattr("src.gui.app.CorpusInitializer", _RecordingInitializer)
    source = tmp_path / "Corpora"
    processed = tmp_path / "Corpora_modified"
    source.mkdir()

    gui.enter(gui.app.source_root, str(source))
    gui.enter(gui.app.processed_root, str(processed))
    assert gui.field(gui.app.source_root) == str(source)
    assert gui.field(gui.app.processed_root) == str(processed)

    gui.tap(t("gui.button.initialize_corpora"))
    gui.pump_and_settle()

    assert "Starting corpus initialization..." in gui.log_text()
    assert "initialized corpora" in gui.log_text()
    assert "Initialization completed." in gui.log_text()
    assert "Brent, Post" in gui.log_text()
    assert gui.visible("Brent")
    assert gui.visible("Post")
    assert not gui.is_enabled("Brent")
    assert gui.status() == t("gui.status.ready")

    gui.tap(t("gui.button.run_analysis"))
    gui.pump_and_settle()

    all_corpora = gui.analysis.commands[0]
    assert _mode(all_corpora) == "tokens"
    assert _values(all_corpora, "--corpus") == []
    assert _values(all_corpora, "--processed-root") == [str(processed)]
    assert _values(all_corpora, "--output-dir") == [DEFAULT_TOKENS_OUTPUT_DIR]
    assert "--generate-plots" not in all_corpora
    assert gui.analysis.working_directories[0] == _project_root()
    assert "for all corpora" in gui.log_text()
    assert "Token analysis completed." in gui.log_text()

    gui.tap(t("gui.checkbox.all_corpora"))
    assert gui.is_enabled("Brent")
    assert gui.is_enabled("Post")
    gui.tap("Brent")
    assert gui.is_selected("Brent")
    assert not gui.is_selected("Post")

    gui.tap(t("gui.button.run_analysis"))
    gui.pump_and_settle()

    one_corpus = gui.analysis.commands[1]
    assert _values(one_corpus, "--corpus") == ["Brent"]
    assert "for Brent" in gui.log_text()

    gui.tap(t("gui.button.generate_plots"))
    gui.pump_and_settle()

    plots = gui.analysis.commands[2]
    assert "--generate-plots" in plots
    assert _values(plots, "--corpus") == ["Brent"]
    assert _values(plots, "--plots-dir") == [
        f"{DEFAULT_TOKENS_OUTPUT_DIR}/iconic_vs_noniconic"
    ]
    assert _values(plots, "--distribution-dir") == [
        f"{DEFAULT_TOKENS_OUTPUT_DIR}/distribution"
    ]
    assert "Token plot generation completed." in gui.log_text()
    assert "token-plots" in gui.log_text()
    assert "token-dist" in gui.log_text()
    assert gui.status() == t("gui.status.ready")
    assert gui.dialogs.entries == []


def test_types_workflow_ends_in_iconicity_export(gui, tmp_path):
    _processed = _prepare_processed_corpus(gui, tmp_path, "Brent", "Post")
    quarterly = tmp_path / "quarterly_grammatical_categories"
    (quarterly / "children" / "WordCount").mkdir(parents=True)
    rated_output = tmp_path / "rated_out"

    gui.tap("Types")

    assert gui.app.mode.get() == "types"
    assert gui.visible(t("gui.section.grammatical_categories"))
    assert gui.visible(t("gui.section.type_count"))
    assert gui.field(gui.app.output_dir) == DEFAULT_TYPES_OUTPUT_DIR
    assert not gui.is_enabled("noun")

    gui.tap(t("gui.checkbox.all_categories"))
    assert gui.is_enabled("noun")
    gui.tap("noun")
    gui.tap("verb")
    gui.tap(t("gui.radio.once_per_form"))
    assert gui.is_selected("noun")
    assert gui.is_selected("verb")
    assert gui.app.type_count_mode.get() == TYPE_COUNT_ONLY_ONCE

    gui.tap(t("gui.button.run_analysis"))
    gui.pump_and_settle()

    types_command = gui.analysis.commands[0]
    assert _mode(types_command) == "types"
    assert _values(types_command, "--category") == ["noun", "verb"]
    assert _values(types_command, "--type-count-mode") == [TYPE_COUNT_ONLY_ONCE]
    assert _values(types_command, "--output-dir") == [DEFAULT_TYPES_OUTPUT_DIR]
    assert "--generate-plots" not in types_command
    assert "Types analysis completed." in gui.log_text()

    gui.tap(t("gui.button.generate_plots"))
    gui.pump_and_settle()

    plots = gui.analysis.commands[1]
    assert "--generate-plots" in plots
    assert _values(plots, "--category") == ["noun", "verb"]
    assert "Types plot generation completed." in gui.log_text()
    assert "types-plots" in gui.log_text()

    assert gui.visible_text_containing(t("gui.rated.no_data"))
    assert not gui.is_enabled(t("gui.button.run_export"))

    gui.enter(gui.app.rated_output_dir, str(rated_output))
    gui.queue_directory(str(quarterly))
    gui.tap(
        t("gui.button.browse"),
        root=gui.section(t("gui.section.rated")),
    )
    gui.pump_and_settle()

    assert gui.field(gui.app.rated_source_dir) == str(quarterly)
    assert gui.visible_text_containing(t("gui.rated.data_found", path=str(quarterly)))
    assert gui.is_enabled(t("gui.button.run_export"))

    gui.tap(t("gui.button.run_export"))
    gui.pump_and_settle()

    export_command = gui.analysis.commands[2]
    assert _mode(export_command) == "rated"
    assert _values(export_command, "--processed-root") == [str(quarterly)]
    assert _values(export_command, "--output-dir") == [str(rated_output)]
    assert _values(export_command, "--corpus") == []
    assert "Iconicity export completed." in gui.log_text()
    assert str(rated_output) in gui.log_text()
    assert gui.status() == t("gui.status.ready")
    assert gui.dialogs.entries == []


def test_failed_analysis_reports_the_exit_code(gui, tmp_path):
    processed = _prepare_processed_corpus(gui, tmp_path, "Brent")
    gui.analysis.return_code = 1

    gui.tap(t("gui.button.run_analysis"))
    gui.pump_and_settle()

    gui.expect_dialog(
        "error",
        t("gui.error.analysis"),
        t("gui.error.external_exit", code=1),
    )
    assert _values(gui.analysis.commands[0], "--processed-root") == [str(processed)]
    assert gui.status() == t("gui.status.ready")
    assert gui.is_enabled(t("gui.button.run_analysis"))


def test_window_stays_busy_until_the_analysis_finishes(gui, tmp_path):
    _prepare_processed_corpus(gui, tmp_path, "Brent")
    gui.analysis.release.clear()

    gui.tap(t("gui.button.run_analysis"))

    assert gui.status() == t("gui.status.in_progress")
    assert not gui.is_enabled(t("gui.button.run_analysis"))
    assert not gui.is_enabled(t("gui.button.generate_plots"))
    assert not gui.is_enabled(t("gui.button.show_initialized"))
    gui.pump_for(0.3)
    assert gui.status() == t("gui.status.in_progress")

    gui.analysis.release.set()
    gui.pump_and_settle()

    assert gui.status() == t("gui.status.ready")
    assert gui.is_enabled(t("gui.button.run_analysis"))
    assert len(gui.analysis.commands) == 1
    assert gui.dialogs.entries == []


def _prepare_processed_corpus(gui, tmp_path, *names):
    source = tmp_path / "Corpora"
    processed = tmp_path / "Corpora_modified"
    source.mkdir()
    processed.mkdir()
    for name in names:
        (processed / name).mkdir()

    gui.enter(gui.app.source_root, str(source))
    gui.enter(gui.app.processed_root, str(processed))
    gui.tap(t("gui.button.show_initialized"))
    return processed


def _mode(command):
    for index, part in enumerate(command):
        if str(part).endswith("gui_analysis_runner.py"):
            return command[index + 1]
    raise AssertionError(f"Analysis runner missing from {command}")


def _values(command, flag):
    values = []
    take_next = False
    for part in command:
        if take_next:
            values.append(part)
            take_next = False
            continue
        if part == flag:
            take_next = True
    return values
