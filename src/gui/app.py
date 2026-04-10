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
from src.gui.services import (
    DEFAULT_DISTRIBUTION_DIR,
    DEFAULT_PLOTS_DIR,
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


class ChildConicityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChildConicity")
        self.geometry("980x760")

        self.source_root = tk.StringVar(value="Corpus")
        self.processed_root = tk.StringVar(value="Corpus_modified")
        self.output_dir = tk.StringVar(value=DEFAULT_TOKENS_OUTPUT_DIR)
        self.mode = tk.StringVar(value="tokens")
        self.all_categories = tk.BooleanVar(value=True)
        self.type_count_mode = tk.StringVar(value=DEFAULT_TYPE_COUNT_MODE)
        self.status_text = tk.StringVar(value="Listo.")

        self._log_queue = queue.Queue()
        self._busy = False
        self._busy_widgets = []
        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill="both", expand=True)

        paths_frame = ttk.LabelFrame(main_frame, text="Rutas", padding=10)
        paths_frame.pack(fill="x")
        self._build_paths_ui(paths_frame)

        corpus_frame = ttk.LabelFrame(main_frame, text="Corpus", padding=10)
        corpus_frame.pack(fill="both", expand=False, pady=(12, 0))
        self._build_corpus_ui(corpus_frame)

        mode_frame = ttk.LabelFrame(main_frame, text="Modo de análisis", padding=10)
        mode_frame.pack(fill="x", pady=(12, 0))
        self._build_mode_ui(mode_frame)

        self.types_frame = ttk.LabelFrame(
            main_frame, text="Categorías gramaticales", padding=10
        )
        self.types_frame.pack(fill="both", expand=False, pady=(12, 0))
        self._build_types_ui(self.types_frame)

        self.type_count_frame = ttk.LabelFrame(
            main_frame, text="Cómo contar en las gráficas de types", padding=10
        )
        self.type_count_frame.pack(fill="x", pady=(12, 0))
        self._build_type_count_ui(self.type_count_frame)

        self.actions_frame = ttk.Frame(main_frame)
        self.actions_frame.pack(fill="x", pady=(12, 0))
        self._build_actions_ui(self.actions_frame)

        self.log_frame = ttk.LabelFrame(main_frame, text="Registro", padding=10)
        self.log_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.log_text = ScrolledText(self.log_frame, height=18, wrap="word")
        self.log_text.pack(fill="both", expand=True)

        self._sync_mode_ui()

    def _build_paths_ui(self, parent):
        ttk.Label(parent, text="Corpus origen").grid(row=0, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.source_root, width=70).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        source_button = ttk.Button(parent, text="Buscar...", command=self._browse_source_root)
        source_button.grid(
            row=0, column=2
        )
        self._busy_widgets.append(source_button)

        ttk.Label(parent, text="Corpus procesado").grid(row=1, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.processed_root, width=70).grid(
            row=1, column=1, sticky="ew", padx=8, pady=(8, 0)
        )
        processed_button = ttk.Button(
            parent, text="Buscar...", command=self._browse_processed_root
        )
        processed_button.grid(
            row=1, column=2, pady=(8, 0)
        )
        self._busy_widgets.append(processed_button)

        parent.columnconfigure(1, weight=1)

    def _build_corpus_ui(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill="x")

        initialize_button = ttk.Button(
            buttons_frame,
            text="Initialize Corpora",
            command=self._start_initialize_corpora,
        )
        initialize_button.pack(side="left")
        self._busy_widgets.append(initialize_button)

        refresh_button = ttk.Button(
            buttons_frame,
            text="Refrescar corpus",
            command=self._refresh_corpora,
        )
        refresh_button.pack(side="left", padx=(8, 0))
        self._busy_widgets.append(refresh_button)

        select_all_button = ttk.Button(
            buttons_frame,
            text="Seleccionar todos",
            command=self._select_all_corpora,
        )
        select_all_button.pack(side="left", padx=(8, 0))
        self._busy_widgets.append(select_all_button)

        ttk.Label(
            parent,
            text="Si no seleccionas ninguno, se usarán todos los corpus disponibles.",
        ).pack(anchor="w", pady=(8, 6))

        self.corpora_listbox = tk.Listbox(
            parent, selectmode=tk.MULTIPLE, exportselection=False, height=6
        )
        self.corpora_listbox.pack(fill="x")
        self.corpora_listbox.bind("<<ListboxSelect>>", lambda _event: self._refresh_categories())

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
        ttk.Label(output_frame, text="Directorio de salida").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=55).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

    def _build_types_ui(self, parent):
        all_categories_check = ttk.Checkbutton(
            parent,
            text="Todas las categorías",
            variable=self.all_categories,
            command=self._sync_categories_ui,
        )
        all_categories_check.pack(anchor="w")
        self._busy_widgets.append(all_categories_check)

        self.categories_listbox = tk.Listbox(
            parent, selectmode=tk.MULTIPLE, exportselection=False, height=8
        )
        self.categories_listbox.pack(fill="x", pady=(8, 0))

    def _build_type_count_ui(self, parent):
        ttk.Label(
            parent,
            text="Elige si las gráficas deben usar las repeticiones reales o contar cada forma solo una vez.",
            wraplength=860,
            justify="left",
        ).pack(anchor="w")

        with_repetitions_radio = ttk.Radiobutton(
            parent,
            text="Con repeticiones",
            value=TYPE_COUNT_WITH_REPETITIONS,
            variable=self.type_count_mode,
        )
        with_repetitions_radio.pack(anchor="w", pady=(8, 0))
        self._busy_widgets.append(with_repetitions_radio)

        only_once_radio = ttk.Radiobutton(
            parent,
            text="Una vez por forma",
            value=TYPE_COUNT_ONLY_ONCE,
            variable=self.type_count_mode,
        )
        only_once_radio.pack(anchor="w", pady=(4, 0))
        self._busy_widgets.append(only_once_radio)

    def _build_actions_ui(self, parent):
        self.run_analysis_button = ttk.Button(
            parent,
            text="Ejecutar análisis",
            command=self._start_run_analysis,
        )
        self.run_analysis_button.pack(side="left")
        self._busy_widgets.append(self.run_analysis_button)

        self.generate_plots_button = ttk.Button(
            parent,
            text="Generar gráficas",
            command=self._start_generate_plots,
        )
        self.generate_plots_button.pack(side="left", padx=(8, 0))
        self._busy_widgets.append(self.generate_plots_button)

        ttk.Label(
            parent,
            textvariable=self.status_text,
        ).pack(side="right")

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

    def _select_all_corpora(self):
        self.corpora_listbox.select_set(0, tk.END)
        self._refresh_categories()

    def _sync_mode_ui(self):
        self.types_frame.pack_forget()
        self.type_count_frame.pack_forget()
        self.actions_frame.pack_forget()
        self.log_frame.pack_forget()

        if self.mode.get() == "types":
            self.types_frame.pack(fill="both", expand=False, pady=(12, 0))
            self.type_count_frame.pack(fill="x", pady=(12, 0))
            if self.output_dir.get() == DEFAULT_TOKENS_OUTPUT_DIR:
                self.output_dir.set(DEFAULT_TYPES_OUTPUT_DIR)
        else:
            if self.output_dir.get() == DEFAULT_TYPES_OUTPUT_DIR:
                self.output_dir.set(DEFAULT_TOKENS_OUTPUT_DIR)

        self.actions_frame.pack(fill="x", pady=(12, 0))
        self.log_frame.pack(fill="both", expand=True, pady=(12, 0))

        self._sync_categories_ui()

    def _sync_categories_ui(self):
        state = tk.DISABLED if self.all_categories.get() else tk.NORMAL
        self.categories_listbox.configure(state=state)

    def _refresh_corpora(self):
        processed_root = self.processed_root.get().strip()
        if not processed_root:
            messagebox.showerror("Error", "Indica primero la ruta de corpus procesado.")
            return

        available_corpora = get_available_corpora(processed_root)
        self.corpora_listbox.delete(0, tk.END)
        for corpus_name in available_corpora:
            self.corpora_listbox.insert(tk.END, corpus_name)

        self._refresh_categories()
        self._append_log(
            f"Corpus disponibles en {processed_root}: "
            + (", ".join(available_corpora) if available_corpora else "(ninguno)")
            + "\n"
        )

    def _refresh_categories(self):
        if self.mode.get() != "types":
            return

        processed_root = self.processed_root.get().strip()
        if not processed_root:
            return

        try:
            categories = get_available_categories(
                processed_root, self._get_selected_corpora()
            )
        except Exception:
            categories = []

        self.categories_listbox.delete(0, tk.END)
        for category in categories:
            self.categories_listbox.insert(tk.END, category)

    def _get_selected_corpora(self):
        selected_indices = self.corpora_listbox.curselection()
        if not selected_indices:
            return None

        return [self.corpora_listbox.get(index) for index in selected_indices]

    def _get_selected_categories(self):
        if self.all_categories.get():
            return None

        selected_indices = self.categories_listbox.curselection()
        if not selected_indices:
            return []

        return [self.categories_listbox.get(index) for index in selected_indices]

    def _start_initialize_corpora(self):
        if self._busy:
            self._notify_busy("Ya hay otra tarea en curso.")
            return
        source_root = self.source_root.get().strip()
        processed_root = self.processed_root.get().strip()
        self._append_log("\nIniciando inicialización de corpus...\n")
        self._run_in_background(
            lambda: self._initialize_corpora_worker(source_root, processed_root)
        )

    def _start_run_analysis(self):
        self._start_analysis_request(generate_plots=False)

    def _start_generate_plots(self):
        self._start_analysis_request(generate_plots=True)

    def _start_analysis_request(self, generate_plots):
        if self._busy:
            self._notify_busy("Ya hay otra tarea en curso.")
            return

        mode = self.mode.get()
        processed_root = self.processed_root.get().strip()
        output_dir = self.output_dir.get().strip()
        selected_corpora = self._get_selected_corpora()
        selected_categories = self._get_selected_categories()
        type_count_mode = self.type_count_mode.get()

        validation_error = self._validate_analysis_inputs(
            processed_root,
            selected_corpora,
        )
        if validation_error is not None:
            messagebox.showerror("Error", validation_error)
            return

        if mode == "types" and selected_categories == []:
            messagebox.showerror(
                "Error",
                "Selecciona al menos una categoría o marca 'Todas las categorías'.",
            )
            return

        action_text = (
            f"generación de gráficas de {mode}"
            if generate_plots
            else f"análisis de {mode}"
        )
        self._append_log(
            "\nLanzando "
            f"{action_text} para "
            f"{', '.join(selected_corpora) if selected_corpora else 'todos los corpus'}...\n"
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
        messagebox.showinfo("En curso", text)

    def _run_in_background(self, worker):
        self._set_busy_state(True, "En curso...")
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _set_busy_state(self, busy, status_text):
        self._busy = busy
        widget_state = tk.DISABLED if busy else tk.NORMAL
        for widget in self._busy_widgets:
            widget.configure(state=widget_state)

        self.corpora_listbox.configure(state=widget_state)
        self.categories_listbox.configure(
            state=tk.DISABLED
            if busy or self.all_categories.get()
            else tk.NORMAL
        )
        self.status_text.set(status_text)

    def _validate_analysis_inputs(self, processed_root, selected_corpora):
        if not processed_root:
            return "Indica primero la ruta de corpus procesado."

        if not os.path.isdir(processed_root):
            return (
                "La carpeta de corpus procesado no existe: "
                f"{processed_root}"
            )

        available_corpora = get_available_corpora(processed_root)
        if not available_corpora:
            return (
                "No hay corpus procesados disponibles en "
                f"{processed_root}. Inicializa o refresca primero."
            )

        if selected_corpora is None:
            return None

        missing_corpora = [
            corpus_name
            for corpus_name in selected_corpora
            if corpus_name not in available_corpora
            or not os.path.isdir(os.path.join(processed_root, corpus_name))
        ]
        if missing_corpora:
            return (
                "Faltan corpus procesados para ejecutar el análisis: "
                + ", ".join(missing_corpora)
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
            self._enqueue_log("\nInicialización completada.\n")
            self._enqueue_callback(self._refresh_corpora)
        except Exception as exc:
            self._enqueue_callback(
                lambda: messagebox.showerror(
                    "Error al inicializar corpus", str(exc)
                )
            )
        finally:
            self._enqueue_callback(lambda: self._set_busy_state(False, "Listo."))

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
                lambda: messagebox.showerror("Error al ejecutar el análisis", str(exc))
            )
        finally:
            self._enqueue_callback(lambda: self._set_busy_state(False, "Listo."))

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
                "Usando interprete para el analisis:",
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

        raise RuntimeError(
            "No hay un interprete disponible con las dependencias necesarias para el análisis."
        )

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

        command = [
            analysis_interpreter,
            "-u",
            _analysis_runner_path(),
            mode,
            "--processed-root",
            processed_root,
            "--output-dir",
            output_dir
            or (
                DEFAULT_TYPES_OUTPUT_DIR
                if mode == "types"
                else DEFAULT_TOKENS_OUTPUT_DIR
            ),
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
        else:
            command.extend(
                [
                    "--plots-dir",
                    DEFAULT_PLOTS_DIR,
                    "--distribution-dir",
                    DEFAULT_DISTRIBUTION_DIR,
                ]
            )

        print("Iniciando proceso externo de análisis...")
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
            print(f"Proceso externo iniciado (PID {process.pid}).")
            if process.stdout is not None:
                for line in process.stdout:
                    print(line, end="")

            return_code = process.wait()
            if return_code != 0:
                raise RuntimeError(
                    f"El analisis externo termino con codigo {return_code}."
                )

            with open(result_path, "r", encoding="utf-8") as file:
                return json.load(file)
        finally:
            if os.path.exists(result_path):
                os.unlink(result_path)

    def _report_analysis_result(self, mode, output_dir, result, generate_plots):
        if mode == "types":
            if generate_plots:
                self._enqueue_log(
                    "\nGeneración de gráficas de types completada.\n"
                )
                self._enqueue_log(
                    "Gráficas de types guardadas en: "
                    f"{result['plot_outputs']['plots_dir']}\n"
                )
            else:
                self._enqueue_log(
                    "\nAnálisis de types completado. Resultados exportados en: "
                    f"{output_dir or DEFAULT_TYPES_OUTPUT_DIR}\n"
                )
            return

        if generate_plots:
            self._enqueue_log(
                "\nGeneración de gráficas de tokens completada.\n"
            )
            self._enqueue_log(
                "Gráficas guardadas en: "
                f"{result['plot_outputs']['plots_dir']} y "
                f"{result['plot_outputs']['distribution_dir']}\n"
            )
            return

        self._enqueue_log(
            "\nAnálisis de tokens completado. Resultados exportados en: "
            f"{output_dir or DEFAULT_TOKENS_OUTPUT_DIR}\n"
        )

    def _enqueue_log(self, text):
        self._log_queue.put(("log", text))

    def _enqueue_callback(self, callback):
        self._log_queue.put(("callback", callback))

    def _poll_log_queue(self):
        while True:
            try:
                item_type, payload = self._log_queue.get_nowait()
            except queue.Empty:
                break

            if item_type == "log":
                self._append_log(payload)
            elif item_type == "callback":
                payload()

        self.after(100, self._poll_log_queue)

    def _append_log(self, text):
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)


def run_app():
    app = ChildConicityApp()
    app.mainloop()
