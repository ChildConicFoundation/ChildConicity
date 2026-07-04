import io
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from contextlib import redirect_stderr, redirect_stdout
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from src.corpus_initialization import CorpusInitializer
from src.i18n import get_locale, save_locale, set_locale, t
from src.gui.services import (
    CORPUS_DATA_ROOT_KEY,
    DEFAULT_DISTRIBUTION_DIR,
    DEFAULT_ICONICITY_CSV,
    DEFAULT_PLOTS_DIR,
    DEFAULT_RATED_OUTPUT_DIR,
    DEFAULT_TOKENS_OUTPUT_DIR,
    DEFAULT_TYPE_COUNT_MODE,
    DEFAULT_TYPES_OUTPUT_DIR,
    TYPE_COUNT_ONLY_ONCE,
    TYPE_COUNT_WITH_REPETITIONS,
    get_available_categories,
    get_available_corpora,
)


class _QueueWriter(io.TextIOBase):
    def __init__(self, callback):
        self._callback = callback

    def write(self, text):
        if text:
            self._callback(text)
        return len(text)

    def flush(self):
        return None


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _has_importable_modules(module_names):
    for module_name in module_names:
        try:
            __import__(module_name)
        except ModuleNotFoundError:
            return False
    return True


def _required_analysis_modules(mode, generate_plots):
    if mode == "tokens":
        required_modules = ["pandas"]
        if generate_plots:
            required_modules.extend(["matplotlib", "numpy", "seaborn"])
        return required_modules

    if mode == "types" and generate_plots:
        return ["pandas", "matplotlib", "numpy", "seaborn"]

    return []


def _analysis_runner_path():
    return os.path.join(_project_root(), "src", "gui_analysis_runner.py")


def _venv_python_path():
    return os.path.join(_project_root(), ".venv", "bin", "python")


def _token_plot_directories(output_dir):
    base_output_dir = output_dir or DEFAULT_TOKENS_OUTPUT_DIR
    return (
        os.path.join(base_output_dir, DEFAULT_PLOTS_DIR),
        os.path.join(base_output_dir, DEFAULT_DISTRIBUTION_DIR),
    )


def _interpreter_supports_modules(python_executable, module_names):
    if not module_names:
        return True

    command = [
        python_executable,
        "-c",
        "import importlib.util, sys; sys.exit(0 if all(importlib.util.find_spec(name) for name in sys.argv[1:]) else 1)",
        *module_names,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def _get_analysis_interpreter(mode, generate_plots):
    required_modules = _required_analysis_modules(mode, generate_plots)
    venv_python = _venv_python_path()
    if os.path.exists(venv_python) and _interpreter_supports_modules(
        venv_python,
        required_modules,
    ):
        return venv_python

    if _interpreter_supports_modules(sys.executable, required_modules):
        return sys.executable

    if _has_importable_modules(required_modules):
        return sys.executable

    return None


CORPUS_COLUMN_COUNT = 3
CATEGORY_COLUMN_COUNT = 3

LOCALE_DISPLAY = {
    "en": "English",
    "es": "Español",
}
DISPLAY_LOCALE = {label: code for code, label in LOCALE_DISPLAY.items()}


class ChildConicityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChildConicity")
        self.geometry("980x720")

        self.source_root = tk.StringVar(value="Corpora")
        self.processed_root = tk.StringVar(value="Corpora_modified")
        self.output_dir = tk.StringVar(value=DEFAULT_TOKENS_OUTPUT_DIR)
        self.rated_source_dir = tk.StringVar(value=DEFAULT_TYPES_OUTPUT_DIR)
        self.rated_output_dir = tk.StringVar(value=DEFAULT_RATED_OUTPUT_DIR)
        self.mode = tk.StringVar(value="tokens")
        self.all_corpora = tk.BooleanVar(value=True)
        self.all_categories = tk.BooleanVar(value=True)
        self.type_count_mode = tk.StringVar(value=DEFAULT_TYPE_COUNT_MODE)
        self.talkbank_email = tk.StringVar(value="")
        self.talkbank_password = tk.StringVar(value="")
        self.status_text = tk.StringVar(value=t("gui.status.ready"))
        self.language_display = tk.StringVar(
            value=LOCALE_DISPLAY.get(get_locale(), LOCALE_DISPLAY["en"])
        )
        self.corpora_vars = {}
        self.corpus_checkbuttons = []
        self.category_vars = {}
        self.category_checkbuttons = []
        self._is_closing = False
        self._i18n_bindings = []

        self._log_queue = queue.Queue()
        self._busy = False
        self._busy_widgets = []
        self.protocol("WM_DELETE_WINDOW", self._handle_close)
        self._build_ui()
        self._poll_log_queue()
        self.after(0, self._initialize_available_data)

    def _bind_i18n(self, widget, key, attr="text", **kwargs):
        self._i18n_bindings.append((widget, key, attr, kwargs))
        widget.configure(**{attr: t(key, **kwargs)})
        return widget

    def _apply_translations(self):
        for widget, key, attr, kwargs in self._i18n_bindings:
            if widget.winfo_exists():
                widget.configure(**{attr: t(key, **kwargs)})

        if self._busy:
            self.status_text.set(t("gui.status.in_progress"))
        else:
            self.status_text.set(t("gui.status.ready"))

        processed_root = self.processed_root.get().strip()
        if processed_root and os.path.isdir(processed_root):
            available_corpora = get_available_corpora(processed_root)
            selected_corpora = set(self._get_selected_corpora() or [])
            self._rebuild_corpora_checkboxes(available_corpora, selected_corpora)
            if self.mode.get() == "types":
                self._refresh_categories()
        else:
            empty_message = t("gui.empty.processed_not_found")
            self._rebuild_corpora_checkboxes([], set(), empty_message=empty_message)
            self._rebuild_category_checkboxes([], set(), empty_message=empty_message)

        self._check_rated_availability()

    def _on_language_changed(self, _event=None):
        locale = DISPLAY_LOCALE.get(self.language_display.get())
        if locale is None or locale == get_locale():
            return

        set_locale(locale)
        save_locale(locale)
        self._apply_translations()

    def _analysis_action_text(self, mode, generate_plots):
        if generate_plots:
            return t(f"gui.action.{mode}_plot_generation")
        return t(f"gui.action.{mode}_analysis")

    def _build_ui(self):
        outer_frame = ttk.Frame(self)
        outer_frame.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(outer_frame, highlightthickness=0)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.main_scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",
            command=self.main_canvas.yview,
        )
        self.main_scrollbar.pack(side="right", fill="y")

        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        main_frame = ttk.Frame(self.main_canvas, padding=12)
        self.main_canvas_window = self.main_canvas.create_window(
            (0, 0),
            window=main_frame,
            anchor="nw",
        )
        main_frame.bind("<Configure>", self._on_main_frame_configure)
        self.main_canvas.bind("<Configure>", self._on_main_canvas_configure)

        language_frame = ttk.Frame(main_frame)
        language_frame.pack(fill="x", pady=(0, 12))
        self._bind_i18n(
            ttk.Label(language_frame, text="Language"),
            "gui.language",
        )
        language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_display,
            values=list(LOCALE_DISPLAY.values()),
            state="readonly",
            width=12,
        )
        language_combo.pack(side="left", padx=(8, 0))
        language_combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        download_frame = ttk.LabelFrame(main_frame, text="Downloads", padding=10)
        download_frame.pack(fill="x")
        self._bind_i18n(download_frame, "gui.section.downloads")
        self._build_download_ui(download_frame)

        paths_frame = ttk.LabelFrame(main_frame, text="Paths", padding=10)
        paths_frame.pack(fill="x", pady=(12, 0))
        self._bind_i18n(paths_frame, "gui.section.paths")
        self._build_paths_ui(paths_frame)

        corpus_frame = ttk.LabelFrame(main_frame, text="Corpus", padding=10)
        corpus_frame.pack(fill="both", expand=False, pady=(12, 0))
        self._bind_i18n(corpus_frame, "gui.section.corpus")
        self._build_corpus_ui(corpus_frame)

        mode_frame = ttk.LabelFrame(main_frame, text="Analysis mode", padding=10)
        mode_frame.pack(fill="x", pady=(12, 0))
        self._bind_i18n(mode_frame, "gui.section.analysis_mode")
        self._build_mode_ui(mode_frame)

        self.types_frame = ttk.LabelFrame(
            main_frame, text="Grammatical categories", padding=10
        )
        self.types_frame.pack(fill="both", expand=False, pady=(12, 0))
        self._bind_i18n(self.types_frame, "gui.section.grammatical_categories")
        self._build_types_ui(self.types_frame)

        self.type_count_frame = ttk.LabelFrame(
            main_frame, text="How to count in type plots", padding=10
        )
        self.type_count_frame.pack(fill="x", pady=(12, 0))
        self._bind_i18n(self.type_count_frame, "gui.section.type_count")
        self._build_type_count_ui(self.type_count_frame)

        self.actions_frame = ttk.Frame(main_frame)
        self.actions_frame.pack(fill="x", pady=(12, 0))
        self._build_actions_ui(self.actions_frame)

        self.rated_frame = ttk.LabelFrame(
            main_frame, text="Iconicity export (requires Types)", padding=10
        )
        self.rated_frame.pack(fill="x", pady=(12, 0))
        self._bind_i18n(self.rated_frame, "gui.section.rated")
        self._build_rated_ui(self.rated_frame)

        self.log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        self.log_frame.pack(fill="both", expand=True, pady=(12, 0))
        self._bind_i18n(self.log_frame, "gui.section.log")
        self.log_text = ScrolledText(self.log_frame, height=12, wrap="word")
        self.log_text.pack(fill="both", expand=True)

        self._sync_mode_ui()

    def _build_download_ui(self, parent):
        self._bind_i18n(
            ttk.Label(parent, text="Email TalkBank"),
            "gui.label.email_talkbank",
        ).grid(row=0, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.talkbank_email, width=50).grid(
            row=0, column=1, sticky="ew", padx=8
        )

        self._bind_i18n(
            ttk.Label(parent, text="Password"),
            "gui.label.password",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(parent, textvariable=self.talkbank_password, show="*", width=50).grid(
            row=1, column=1, sticky="ew", padx=8, pady=(8, 0)
        )

        download_btn = ttk.Button(
            parent,
            text="Download corpora",
            command=self._start_download_corpora,
        )
        self._bind_i18n(download_btn, "gui.button.download_corpora")
        download_btn.grid(row=2, column=0, sticky="w", pady=(10, 0))
        self._busy_widgets.append(download_btn)

        iconicity_download_btn = ttk.Button(
            parent,
            text="Download iconicity ratings",
            command=self._start_download_iconicity_ratings,
        )
        self._bind_i18n(iconicity_download_btn, "gui.button.download_ratings")
        iconicity_download_btn.grid(row=2, column=1, sticky="w", padx=8, pady=(10, 0))
        self._busy_widgets.append(iconicity_download_btn)

        parent.columnconfigure(1, weight=1)

    def _build_paths_ui(self, parent):
        self._bind_i18n(
            ttk.Label(parent, text="Source corpus"),
            "gui.label.source_corpus",
        ).grid(row=0, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.source_root, width=70).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        source_button = ttk.Button(parent, text="Browse...", command=self._browse_source_root)
        self._bind_i18n(source_button, "gui.button.browse")
        source_button.grid(
            row=0, column=2
        )
        self._busy_widgets.append(source_button)

        self._bind_i18n(
            ttk.Label(parent, text="Processed corpus"),
            "gui.label.processed_corpus",
        ).grid(row=1, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.processed_root, width=70).grid(
            row=1, column=1, sticky="ew", padx=8, pady=(8, 0)
        )
        processed_button = ttk.Button(
            parent, text="Browse...", command=self._browse_processed_root
        )
        self._bind_i18n(processed_button, "gui.button.browse")
        processed_button.grid(
            row=1, column=2, pady=(8, 0)
        )
        self._busy_widgets.append(processed_button)

        parent.columnconfigure(1, weight=1)

    def _build_corpus_ui(self, parent):
        all_corpora_check = ttk.Checkbutton(
            parent,
            text="All corpora",
            variable=self.all_corpora,
            command=self._sync_corpora_ui,
        )
        self._bind_i18n(all_corpora_check, "gui.checkbox.all_corpora")
        all_corpora_check.pack(anchor="w")
        self._busy_widgets.append(all_corpora_check)

        self._bind_i18n(
            ttk.Label(
                parent,
                text="Select one or more corpora using the checkboxes:",
            ),
            "gui.help.corpora_select",
        ).pack(anchor="w", pady=(8, 4))

        corpora_container = ttk.Frame(parent)
        corpora_container.pack(fill="both", expand=False)

        self.corpora_canvas = tk.Canvas(
            corpora_container,
            height=120,
            highlightthickness=0,
        )
        self.corpora_canvas.pack(side="left", fill="both", expand=True)

        self.corpora_scrollbar = ttk.Scrollbar(
            corpora_container,
            orient="vertical",
            command=self.corpora_canvas.yview,
        )
        self.corpora_scrollbar.pack(side="right", fill="y")

        self.corpora_canvas.configure(
            yscrollcommand=self.corpora_scrollbar.set
        )

        self.corpora_inner_frame = ttk.Frame(self.corpora_canvas)
        self.corpora_canvas_window = self.corpora_canvas.create_window(
            (0, 0),
            window=self.corpora_inner_frame,
            anchor="nw",
        )
        self.corpora_inner_frame.bind(
            "<Configure>",
            self._on_corpora_frame_configure,
        )
        self.corpora_canvas.bind(
            "<Configure>",
            self._on_corpora_canvas_configure,
        )
        self._rebuild_corpora_checkboxes(
            [],
            selected_corpora=set(),
            empty_message=t("gui.empty.click_show_corpora"),
        )

        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill="x", pady=(10, 0))

        initialize_button = ttk.Button(
            buttons_frame,
            text="Initialize corpora",
            command=self._start_initialize_corpora,
        )
        self._bind_i18n(initialize_button, "gui.button.initialize_corpora")
        initialize_button.pack(side="left")
        self._busy_widgets.append(initialize_button)

        refresh_button = ttk.Button(
            buttons_frame,
            text="Show initialized corpora",
            command=self._refresh_corpora,
        )
        self._bind_i18n(refresh_button, "gui.button.show_initialized")
        refresh_button.pack(side="left", padx=(8, 0))
        self._busy_widgets.append(refresh_button)

    def _build_mode_ui(self, parent):
        radio_frame = ttk.Frame(parent)
        radio_frame.pack(fill="x")

        tokens_radio = ttk.Radiobutton(
            radio_frame,
            text="Tokens",
            value="tokens",
            variable=self.mode,
            command=self._sync_mode_ui,
        )
        tokens_radio.pack(side="left")
        self._busy_widgets.append(tokens_radio)

        types_radio = ttk.Radiobutton(
            radio_frame,
            text="Types",
            value="types",
            variable=self.mode,
            command=self._sync_mode_ui,
        )
        types_radio.pack(side="left", padx=(12, 0))
        self._busy_widgets.append(types_radio)


        output_frame = ttk.Frame(parent)
        output_frame.pack(fill="x", pady=(10, 0))
        self._bind_i18n(
            ttk.Label(output_frame, text="Output directory"),
            "gui.label.output_directory",
        ).pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=55).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

    def _build_rated_ui(self, parent):
        self._bind_i18n(
            ttk.Label(
                parent,
                text=t("gui.help.rated"),
                wraplength=860,
                justify="left",
            ),
            "gui.help.rated",
        ).pack(anchor="w")

        source_frame = ttk.Frame(parent)
        source_frame.pack(fill="x", pady=(10, 0))
        self._bind_i18n(
            ttk.Label(source_frame, text="Quarterly data"),
            "gui.label.quarterly_data",
        ).pack(side="left")
        ttk.Entry(source_frame, textvariable=self.rated_source_dir, width=55).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )
        browse_btn = ttk.Button(
            source_frame,
            text="Browse...",
            command=self._browse_rated_source_dir_and_refresh,
        )
        self._bind_i18n(browse_btn, "gui.button.browse")
        browse_btn.pack(side="left", padx=(8, 0))
        self._busy_widgets.append(browse_btn)

        output_frame = ttk.Frame(parent)
        output_frame.pack(fill="x", pady=(8, 0))
        self._bind_i18n(
            ttk.Label(output_frame, text="Output directory"),
            "gui.label.output_directory",
        ).pack(side="left")
        ttk.Entry(output_frame, textvariable=self.rated_output_dir, width=55).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

        self.rated_status_label = ttk.Label(parent, text="", foreground="gray")
        self.rated_status_label.pack(anchor="w", pady=(4, 0))

        self.rated_run_button = ttk.Button(
            parent,
            text="Run export",
            command=self._start_rated_export,
            state=tk.DISABLED,
        )
        self._bind_i18n(self.rated_run_button, "gui.button.run_export")
        self.rated_run_button.pack(anchor="w", pady=(8, 0))

    def _build_types_ui(self, parent):
        all_categories_check = ttk.Checkbutton(
            parent,
            text="All categories",
            variable=self.all_categories,
            command=self._sync_categories_ui,
        )
        self._bind_i18n(all_categories_check, "gui.checkbox.all_categories")
        all_categories_check.pack(anchor="w")
        self._busy_widgets.append(all_categories_check)

        self._bind_i18n(
            ttk.Label(
                parent,
                text="Select one or more categories using the checkboxes:",
            ),
            "gui.help.categories_select",
        ).pack(anchor="w", pady=(8, 4))

        categories_container = ttk.Frame(parent)
        categories_container.pack(fill="both", expand=False)

        self.categories_canvas = tk.Canvas(
            categories_container,
            height=130,
            highlightthickness=0,
        )
        self.categories_canvas.pack(side="left", fill="both", expand=True)

        self.categories_scrollbar = ttk.Scrollbar(
            categories_container,
            orient="vertical",
            command=self.categories_canvas.yview,
        )
        self.categories_scrollbar.pack(side="right", fill="y")

        self.categories_canvas.configure(
            yscrollcommand=self.categories_scrollbar.set
        )

        self.categories_inner_frame = ttk.Frame(self.categories_canvas)
        self.categories_canvas_window = self.categories_canvas.create_window(
            (0, 0),
            window=self.categories_inner_frame,
            anchor="nw",
        )
        self.categories_inner_frame.bind(
            "<Configure>",
            self._on_categories_frame_configure,
        )
        self.categories_canvas.bind(
            "<Configure>",
            self._on_categories_canvas_configure,
        )
        self._rebuild_category_checkboxes(
            [],
            selected_categories=set(),
            empty_message=t("gui.empty.click_show_or_wait"),
        )

        self.types_actions_frame = ttk.Frame(parent)
        self.types_actions_frame.pack(fill="x", pady=(10, 0))

        self.types_run_analysis_button = ttk.Button(
            self.types_actions_frame,
            text="Run analysis",
            command=self._start_run_analysis,
        )
        self._bind_i18n(self.types_run_analysis_button, "gui.button.run_analysis")
        self.types_run_analysis_button.pack(anchor="w")
        self._busy_widgets.append(self.types_run_analysis_button)

    def _build_type_count_ui(self, parent):
        self._bind_i18n(
            ttk.Label(
                parent,
                text=t("gui.help.type_count"),
                wraplength=860,
                justify="left",
            ),
            "gui.help.type_count",
        ).pack(anchor="w")

        with_repetitions_radio = ttk.Radiobutton(
            parent,
            text="With repetitions",
            value=TYPE_COUNT_WITH_REPETITIONS,
            variable=self.type_count_mode,
        )
        self._bind_i18n(with_repetitions_radio, "gui.radio.with_repetitions")
        with_repetitions_radio.pack(anchor="w", pady=(8, 0))
        self._busy_widgets.append(with_repetitions_radio)

        only_once_radio = ttk.Radiobutton(
            parent,
            text="Once per form",
            value=TYPE_COUNT_ONLY_ONCE,
            variable=self.type_count_mode,
        )
        self._bind_i18n(only_once_radio, "gui.radio.once_per_form")
        only_once_radio.pack(anchor="w", pady=(4, 0))
        self._busy_widgets.append(only_once_radio)

    def _build_actions_ui(self, parent):
        self.run_analysis_button = ttk.Button(
            parent,
            text="Run analysis",
            command=self._start_run_analysis,
        )
        self._bind_i18n(self.run_analysis_button, "gui.button.run_analysis")
        self.run_analysis_button.pack(side="left")
        self._busy_widgets.append(self.run_analysis_button)

        self.generate_plots_button = ttk.Button(
            parent,
            text="Generate plots",
            command=self._start_generate_plots,
        )
        self._bind_i18n(self.generate_plots_button, "gui.button.generate_plots")
        self.generate_plots_button.pack(side="left", padx=(8, 0))
        self._busy_widgets.append(self.generate_plots_button)

        ttk.Label(
            parent,
            textvariable=self.status_text,
        ).pack(side="right")

    def _start_download_corpora(self):
        if self._busy:
            self._notify_busy(t("gui.notify.busy"))
            return

        email = self.talkbank_email.get().strip()
        password = self.talkbank_password.get()
        output_dir = self.source_root.get().strip() or "Corpora"

        if not email or not password:
            messagebox.showerror(
                t("gui.error.title"),
                t("gui.error.talkbank_credentials"),
            )
            return

        self._append_log(t("gui.log.download_corpora_start"))
        self._run_in_background(
            lambda: self._download_corpora_worker(email, password, output_dir)
        )

    def _download_corpora_worker(self, email, password, output_dir):
        from src.cli.download_corpora import run as download_run
        writer = _QueueWriter(self._enqueue_log)
        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                download_run(
                    email=email,
                    password=password,
                    corpora_filter=None,
                    output_dir=output_dir,
                    force=False,
                )
            self._enqueue_log(t("gui.log.download_complete"))
            self._enqueue_callback(self._refresh_corpora)
        except Exception as exc:
            self._enqueue_callback(
                lambda e=exc: messagebox.showerror(t("gui.error.corpus_download"), str(e))
            )
        finally:
            self._enqueue_callback(
                lambda: self._set_busy_state(False, t("gui.status.ready"))
            )

    def _start_download_iconicity_ratings(self):
        if self._busy:
            self._notify_busy(t("gui.notify.busy"))
            return

        output_path = os.path.join(_project_root(), DEFAULT_ICONICITY_CSV)
        self._append_log(t("gui.log.ratings_download_start"))
        self._run_in_background(
            lambda: self._download_iconicity_ratings_worker(output_path)
        )

    def _download_iconicity_ratings_worker(self, output_path):
        from src.cli.download_iconicity_ratings import download_iconicity_ratings

        writer = _QueueWriter(self._enqueue_log)
        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                download_iconicity_ratings(output_path=output_path, force=True)
            self._enqueue_log(t("gui.log.ratings_download_complete"))
        except Exception as exc:
            self._enqueue_callback(
                lambda e=exc: messagebox.showerror(
                    t("gui.error.ratings_download"), str(e)
                )
            )
        finally:
            self._enqueue_callback(
                lambda: self._set_busy_state(False, t("gui.status.ready"))
            )

    def _browse_source_root(self):
        selected_dir = filedialog.askdirectory(initialdir=self.source_root.get() or ".")
        if selected_dir:
            self.source_root.set(selected_dir)

    def _browse_processed_root(self):
        selected_dir = filedialog.askdirectory(
            initialdir=self.processed_root.get() or "."
        )
        if selected_dir:
            self.processed_root.set(selected_dir)
            self._refresh_corpora()

    def _browse_rated_source_dir_and_refresh(self):
        selected_dir = filedialog.askdirectory(
            initialdir=self.rated_source_dir.get() or "."
        )
        if selected_dir:
            self.rated_source_dir.set(selected_dir)
            self._check_rated_availability()

    def _check_rated_availability(self):
        source = self.rated_source_dir.get().strip()
        has_data = (
            bool(source)
            and os.path.isdir(source)
            and any(
                (p / "WordCount").is_dir()
                for p in __import__("pathlib").Path(source).iterdir()
                if p.is_dir()
            )
        )
        if has_data:
            self.rated_status_label.configure(
                text=t("gui.rated.data_found", path=source),
                foreground="green",
            )
            if not self._busy:
                self.rated_run_button.configure(state=tk.NORMAL)
        else:
            self.rated_status_label.configure(
                text=t("gui.rated.no_data"),
                foreground="red",
            )
            self.rated_run_button.configure(state=tk.DISABLED)

    def _start_rated_export(self):
        if self._busy:
            self._notify_busy(t("gui.notify.busy"))
            return

        rated_source = self.rated_source_dir.get().strip()
        output_dir = self.rated_output_dir.get().strip() or DEFAULT_RATED_OUTPUT_DIR

        self._append_log(t("gui.log.iconicity_export_start"))
        self._run_in_background(
            lambda: self._run_analysis_worker(
                mode="rated",
                processed_root=rated_source,
                output_dir=output_dir,
                generate_plots=False,
                selected_corpora=None,
                selected_categories=None,
                type_count_mode=DEFAULT_TYPE_COUNT_MODE,
            )
        )

    def _handle_close(self):
        self._is_closing = True
        self.destroy()

    def _initialize_available_data(self):
        processed_root = self.processed_root.get().strip()
        if not processed_root or not os.path.isdir(processed_root):
            self._rebuild_corpora_checkboxes(
                [],
                selected_corpora=set(),
                empty_message=t("gui.empty.processed_not_found"),
            )
            self._rebuild_category_checkboxes(
                [],
                selected_categories=set(),
                empty_message=t("gui.empty.processed_not_found"),
            )
            return

        self._refresh_corpora()
        self._check_rated_availability()

    def _on_categories_frame_configure(self, _event):
        self.categories_canvas.configure(
            scrollregion=self.categories_canvas.bbox("all")
        )

    def _on_corpora_frame_configure(self, _event):
        self.corpora_canvas.configure(
            scrollregion=self.corpora_canvas.bbox("all")
        )

    def _on_main_frame_configure(self, _event):
        self.main_canvas.configure(
            scrollregion=self.main_canvas.bbox("all")
        )

    def _on_main_canvas_configure(self, event):
        self.main_canvas.itemconfigure(
            self.main_canvas_window,
            width=event.width,
        )

    def _on_categories_canvas_configure(self, event):
        self.categories_canvas.itemconfigure(
            self.categories_canvas_window,
            width=event.width,
        )

    def _on_corpora_canvas_configure(self, event):
        self.corpora_canvas.itemconfigure(
            self.corpora_canvas_window,
            width=event.width,
        )

    def _sync_mode_ui(self):
        self.types_frame.pack_forget()
        self.type_count_frame.pack_forget()
        self.actions_frame.pack_forget()
        self.log_frame.pack_forget()
        self.rated_frame.pack_forget()

        self.run_analysis_button.pack_forget()
        self.generate_plots_button.pack_forget()

        mode = self.mode.get()

        if mode == "types":
            self._refresh_categories()
            self.types_frame.pack(fill="both", expand=False, pady=(12, 0))
            self.type_count_frame.pack(fill="x", pady=(12, 0))
            self.generate_plots_button.pack(side="left")
            if self.output_dir.get() == DEFAULT_TOKENS_OUTPUT_DIR:
                self.output_dir.set(DEFAULT_TYPES_OUTPUT_DIR)
        else:
            self.run_analysis_button.pack(side="left")
            self.generate_plots_button.pack(side="left", padx=(8, 0))
            if self.output_dir.get() == DEFAULT_TYPES_OUTPUT_DIR:
                self.output_dir.set(DEFAULT_TOKENS_OUTPUT_DIR)

        self.actions_frame.pack(fill="x", pady=(12, 0))
        self.rated_frame.pack(fill="x", pady=(12, 0))
        self.log_frame.pack(fill="both", expand=True, pady=(12, 0))

        self._sync_corpora_ui()
        self._sync_categories_ui()

    def _sync_corpora_ui(self):
        self._set_corpus_checkbuttons_state(
            tk.DISABLED if self._busy or self.all_corpora.get() else tk.NORMAL
        )
        self._refresh_categories()

    def _sync_categories_ui(self):
        self._set_category_checkbuttons_state(
            tk.DISABLED if self.all_categories.get() else tk.NORMAL
        )

    def _refresh_corpora(self):
        processed_root = self.processed_root.get().strip()
        if not processed_root:
            messagebox.showerror(
                t("gui.error.title"),
                t("gui.error.set_processed_path"),
            )
            return

        available_corpora = get_available_corpora(processed_root)
        selected_corpora = set(self._get_selected_corpora() or [])
        self._rebuild_corpora_checkboxes(available_corpora, selected_corpora)

        self._refresh_categories()
        corpora_list = (
            ", ".join(available_corpora)
            if available_corpora
            else t("gui.common.none")
        )
        self._append_log(
            t(
                "gui.log.corpora_refreshed",
                path=processed_root,
                list=corpora_list,
            )
        )

    def _refresh_categories(self):
        if self.mode.get() != "types":
            return

        processed_root = self.processed_root.get().strip()
        if not processed_root:
            return

        selected_categories = {
            category
            for category, variable in self.category_vars.items()
            if variable.get()
        }

        try:
            categories = get_available_categories(
                processed_root,
                self._get_selected_corpora(),
            )
            self._rebuild_category_checkboxes(categories, selected_categories)
        except Exception as exc:
            self._rebuild_category_checkboxes(
                [],
                selected_categories=set(),
                empty_message=t("gui.log.categories_load_error", error=exc),
            )

    def _get_selected_corpora(self):
        if self.all_corpora.get():
            return None

        selected_corpora = [
            corpus_name
            for corpus_name, variable in self.corpora_vars.items()
            if variable.get()
        ]
        if not selected_corpora:
            return None

        return selected_corpora

    def _get_selected_categories(self):
        if self.all_categories.get():
            return None

        return [
            category
            for category, variable in self.category_vars.items()
            if variable.get()
        ]

    def _rebuild_category_checkboxes(
        self,
        categories,
        selected_categories,
        empty_message=None,
    ):
        if empty_message is None:
            empty_message = t("gui.empty.no_categories")
        for child in self.categories_inner_frame.winfo_children():
            child.destroy()

        self.category_vars = {}
        self.category_checkbuttons = []

        if not categories:
            empty_label = ttk.Label(
                self.categories_inner_frame,
                text=empty_message,
            )
            empty_label.pack(anchor="w")
            self.categories_canvas.configure(scrollregion=(0, 0, 0, 0))
            return

        total_categories = len(categories)
        column_size = (
            total_categories + CATEGORY_COLUMN_COUNT - 1
        ) // CATEGORY_COLUMN_COUNT

        for column in range(CATEGORY_COLUMN_COUNT):
            self.categories_inner_frame.columnconfigure(column, weight=1)

        for index, category in enumerate(categories):
            column = min(index // column_size, CATEGORY_COLUMN_COUNT - 1)
            row = index % column_size

            variable = tk.BooleanVar(value=category in selected_categories)
            checkbutton = ttk.Checkbutton(
                self.categories_inner_frame,
                text=category,
                variable=variable,
            )
            checkbutton.grid(
                row=row,
                column=column,
                sticky="w",
                padx=(0, 16) if column < CATEGORY_COLUMN_COUNT - 1 else (0, 0),
                pady=(0, 2),
            )
            self.category_vars[category] = variable
            self.category_checkbuttons.append(checkbutton)

        self._sync_categories_ui()

    def _rebuild_corpora_checkboxes(
        self,
        corpora,
        selected_corpora,
        empty_message=None,
    ):
        if empty_message is None:
            empty_message = t("gui.empty.no_corpora")
        for child in self.corpora_inner_frame.winfo_children():
            child.destroy()

        self.corpora_vars = {}
        self.corpus_checkbuttons = []

        if not corpora:
            empty_label = ttk.Label(
                self.corpora_inner_frame,
                text=empty_message,
            )
            empty_label.pack(anchor="w")
            self.corpora_canvas.configure(scrollregion=(0, 0, 0, 0))
            return

        total_corpora = len(corpora)
        column_size = (
            total_corpora + CORPUS_COLUMN_COUNT - 1
        ) // CORPUS_COLUMN_COUNT

        for column in range(CORPUS_COLUMN_COUNT):
            self.corpora_inner_frame.columnconfigure(column, weight=1)

        for index, corpus_name in enumerate(corpora):
            column = min(index // column_size, CORPUS_COLUMN_COUNT - 1)
            row = index % column_size

            variable = tk.BooleanVar(value=corpus_name in selected_corpora)
            checkbutton = ttk.Checkbutton(
                self.corpora_inner_frame,
                text=corpus_name,
                variable=variable,
                command=self._refresh_categories,
            )
            checkbutton.grid(
                row=row,
                column=column,
                sticky="w",
                padx=(0, 16) if column < CORPUS_COLUMN_COUNT - 1 else (0, 0),
                pady=(0, 2),
            )
            self.corpora_vars[corpus_name] = variable
            self.corpus_checkbuttons.append(checkbutton)

        self._sync_corpora_ui()

    def _set_corpus_checkbuttons_state(self, state):
        for checkbutton in self.corpus_checkbuttons:
            checkbutton.configure(state=state)

    def _set_category_checkbuttons_state(self, state):
        for checkbutton in self.category_checkbuttons:
            checkbutton.configure(state=state)

    def _start_initialize_corpora(self):
        if self._busy:
            self._notify_busy(t("gui.notify.busy"))
            return
        source_root = self.source_root.get().strip()
        processed_root = self.processed_root.get().strip()
        self._append_log(t("gui.log.init_start"))
        self._run_in_background(
            lambda: self._initialize_corpora_worker(source_root, processed_root)
        )

    def _start_run_analysis(self):
        self._start_analysis_request(generate_plots=False)

    def _start_generate_plots(self):
        self._start_analysis_request(generate_plots=True)

    def _start_analysis_request(self, generate_plots):
        if self._busy:
            self._notify_busy(t("gui.notify.busy"))
            return

        mode = self.mode.get()
        processed_root = self.processed_root.get().strip()
        output_dir = self.output_dir.get().strip()
        selected_corpora = self._get_selected_corpora()
        selected_categories = self._get_selected_categories()
        type_count_mode = self.type_count_mode.get()

        if mode == "rated":
            rated_source = self.rated_source_dir.get().strip()
            if not rated_source or not os.path.isdir(rated_source):
                messagebox.showerror(
                    t("gui.error.title"),
                    t("gui.validation.quarterly_missing", path=rated_source),
                )
                return
        else:
            validation_error = self._validate_analysis_inputs(
                processed_root,
                selected_corpora,
            )
            if validation_error is not None:
                messagebox.showerror(t("gui.error.title"), validation_error)
                return

        if mode == "types" and selected_categories == []:
            messagebox.showerror(
                t("gui.error.title"),
                t("gui.error.select_category"),
            )
            return

        action_text = self._analysis_action_text(mode, generate_plots)
        corpora_text = (
            ", ".join(selected_corpora)
            if selected_corpora
            else t("gui.common.all_corpora")
        )
        self._append_log(
            t(
                "gui.log.analysis_start",
                action=action_text,
                corpora=corpora_text,
            )
        )
        self._run_in_background(
            lambda: self._run_analysis_worker(
                mode=mode,
                processed_root=processed_root,
                output_dir=output_dir,
                generate_plots=generate_plots,
                selected_corpora=selected_corpora,
                selected_categories=selected_categories,
                type_count_mode=type_count_mode,
            )
        )

    def _notify_busy(self, text):
        self._append_log(f"\n{text}\n")
        messagebox.showinfo(t("gui.info.in_progress"), text)

    def _run_in_background(self, worker):
        self._set_busy_state(True, t("gui.status.in_progress"))
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _set_busy_state(self, busy, status_text):
        self._busy = busy
        widget_state = tk.DISABLED if busy else tk.NORMAL
        for widget in self._busy_widgets:
            widget.configure(state=widget_state)

        self._sync_corpora_ui()
        self._set_category_checkbuttons_state(
            tk.DISABLED if busy or self.all_categories.get() else tk.NORMAL
        )
        if busy:
            self.rated_run_button.configure(state=tk.DISABLED)
        else:
            self._check_rated_availability()
        self.status_text.set(status_text)

    def _validate_analysis_inputs(self, processed_root, selected_corpora):
        if not processed_root:
            return t("gui.validation.set_processed_path")

        if os.path.basename(os.path.normpath(processed_root)) != CORPUS_DATA_ROOT_KEY:
            return t(
                "gui.validation.processed_name",
                name=CORPUS_DATA_ROOT_KEY,
            )

        if not os.path.isdir(processed_root):
            return t("gui.validation.processed_missing", path=processed_root)

        available_corpora = get_available_corpora(processed_root)
        if not available_corpora:
            return t("gui.validation.no_corpora", path=processed_root)

        if selected_corpora is None:
            return None

        missing_corpora = [
            corpus_name
            for corpus_name in selected_corpora
            if corpus_name not in available_corpora
            or not os.path.isdir(os.path.join(processed_root, corpus_name))
        ]
        if missing_corpora:
            return t(
                "gui.validation.missing_corpora",
                list=", ".join(missing_corpora),
            )

        return None

    def _initialize_corpora_worker(self, source_root, processed_root):
        writer = _QueueWriter(self._enqueue_log)
        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                initializer = CorpusInitializer(
                    source_root=source_root,
                    output_root=processed_root,
                )
                initializer.initialize_all()
            self._enqueue_log(t("gui.log.init_complete"))
            self._enqueue_callback(self._refresh_corpora)
        except Exception as exc:
            self._enqueue_callback(
                lambda e=exc: messagebox.showerror(
                    t("gui.error.init_corpus"), str(e)
                )
            )
        finally:
            self._enqueue_callback(
                lambda: self._set_busy_state(False, t("gui.status.ready"))
            )

    def _run_analysis_worker(
        self,
        mode,
        processed_root,
        output_dir,
        generate_plots,
        selected_corpora,
        selected_categories,
        type_count_mode,
    ):
        writer = _QueueWriter(self._enqueue_log)

        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                result = self._run_analysis(
                    mode=mode,
                    processed_root=processed_root,
                    output_dir=output_dir,
                    generate_plots=generate_plots,
                    selected_corpora=selected_corpora,
                    selected_categories=selected_categories,
                    type_count_mode=type_count_mode,
                )
                self._report_analysis_result(
                    mode,
                    output_dir,
                    result,
                    generate_plots=generate_plots,
                )
        except Exception as exc:
            self._enqueue_callback(
                lambda e=exc: messagebox.showerror(t("gui.error.analysis"), str(e))
            )
        finally:
            self._enqueue_callback(
                lambda: self._set_busy_state(False, t("gui.status.ready"))
            )
            self._enqueue_callback(self._check_rated_availability)

    def _run_analysis(
        self,
        mode,
        processed_root,
        output_dir,
        generate_plots,
        selected_corpora,
        selected_categories,
        type_count_mode,
    ):
        analysis_interpreter = _get_analysis_interpreter(mode, generate_plots)
        if analysis_interpreter is not None:
            print(
                "Using interpreter for analysis:",
                analysis_interpreter,
            )
            return self._run_analysis_in_subprocess(
                analysis_interpreter=analysis_interpreter,
                mode=mode,
                processed_root=processed_root,
                output_dir=output_dir,
                generate_plots=generate_plots,
                selected_corpora=selected_corpora,
                selected_categories=selected_categories,
                type_count_mode=type_count_mode,
            )

        raise RuntimeError(t("gui.error.no_interpreter"))

    def _run_analysis_in_subprocess(
        self,
        analysis_interpreter,
        mode,
        processed_root,
        output_dir,
        generate_plots,
        selected_corpora,
        selected_categories,
        type_count_mode,
    ):
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json",
        ) as result_file:
            result_path = result_file.name

        if mode == "rated":
            effective_source = self.rated_source_dir.get().strip() or DEFAULT_TYPES_OUTPUT_DIR
        else:
            effective_source = processed_root

        command = [
            analysis_interpreter,
            "-u",
            _analysis_runner_path(),
            mode,
            "--processed-root",
            effective_source,
            "--output-dir",
            output_dir
            or (
                DEFAULT_RATED_OUTPUT_DIR
                if mode == "rated"
                else DEFAULT_TYPES_OUTPUT_DIR
                if mode == "types"
                else DEFAULT_TOKENS_OUTPUT_DIR
            ),
            "--iconicity-csv",
            DEFAULT_ICONICITY_CSV,
            "--result-file",
            result_path,
        ]

        if generate_plots:
            command.append("--generate-plots")

        if selected_corpora:
            for corpus_name in selected_corpora:
                command.extend(["--corpus", corpus_name])

        if mode == "types":
            command.extend(["--type-count-mode", type_count_mode])
            if selected_categories:
                for category in selected_categories:
                    command.extend(["--category", category])
        elif mode != "rated" and generate_plots:
            plots_dir, distribution_dir = _token_plot_directories(output_dir)
            command.extend(
                [
                    "--plots-dir",
                    plots_dir,
                    "--distribution-dir",
                    distribution_dir,
                ]
            )

        print("Starting external analysis process...")
        env = os.environ.copy()
        env.setdefault(
            "MPLCONFIGDIR",
            os.path.join(tempfile.gettempdir(), "childconicity_mpl"),
        )
        os.makedirs(env["MPLCONFIGDIR"], exist_ok=True)

        process = subprocess.Popen(
            command,
            cwd=_project_root(),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        try:
            print(f"External process started (PID {process.pid}).")
            if process.stdout is not None:
                for line in process.stdout:
                    print(line, end="")

            return_code = process.wait()
            if return_code != 0:
                raise RuntimeError(
                    t("gui.error.external_exit", code=return_code)
                )

            with open(result_path, "r", encoding="utf-8") as file:
                return json.load(file)
        finally:
            if os.path.exists(result_path):
                os.unlink(result_path)

    def _report_analysis_result(self, mode, output_dir, result, generate_plots):
        if mode == "rated":
            self._enqueue_log(
                t(
                    "gui.log.iconicity_export_done",
                    path=output_dir or DEFAULT_RATED_OUTPUT_DIR,
                )
            )
            return

        if mode == "types":
            if generate_plots:
                self._enqueue_log(t("gui.log.types_plots_done"))
                self._enqueue_log(t("gui.log.types_plots_count_note"))
                self._enqueue_log(
                    t(
                        "gui.log.types_plots_saved",
                        path=result["plot_outputs"]["plots_dir"],
                    )
                )
            else:
                self._enqueue_log(
                    t(
                        "gui.log.types_analysis_done",
                        path=output_dir or DEFAULT_TYPES_OUTPUT_DIR,
                    )
                )
            return

        if generate_plots:
            self._enqueue_log(t("gui.log.token_plots_done"))
            self._enqueue_log(
                t(
                    "gui.log.plots_saved_pair",
                    plots=result["plot_outputs"]["plots_dir"],
                    distribution=result["plot_outputs"]["distribution_dir"],
                )
            )
            return

        self._enqueue_log(
            t(
                "gui.log.token_analysis_done",
                path=output_dir or DEFAULT_TOKENS_OUTPUT_DIR,
            )
        )

    def _enqueue_log(self, text):
        self._log_queue.put(("log", text))

    def _enqueue_callback(self, callback):
        self._log_queue.put(("callback", callback))

    def _poll_log_queue(self):
        if self._is_closing:
            return

        while True:
            try:
                item_type, payload = self._log_queue.get_nowait()
            except queue.Empty:
                break

            if item_type == "log":
                self._append_log(payload)
            elif item_type == "callback":
                payload()

        if not self._is_closing:
            self.after(100, self._poll_log_queue)

    def _append_log(self, text):
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)


def run_app():
    app = ChildConicityApp()
    app.mainloop()
