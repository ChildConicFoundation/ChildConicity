import io
import queue
import threading
import tkinter as tk
from contextlib import redirect_stderr, redirect_stdout
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from src.corpus_initialization import CorpusInitializer
from src.gui.services import (
    DEFAULT_TOKENS_OUTPUT_DIR,
    DEFAULT_TYPES_OUTPUT_DIR,
    get_available_categories,
    get_available_corpora,
    run_tokens_analysis,
    run_types_analysis,
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
        self.generate_plots = tk.BooleanVar(value=False)

        self._log_queue = queue.Queue()
        self._busy = False
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

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill="x", pady=(12, 0))
        self._build_actions_ui(actions_frame)

        log_frame = ttk.LabelFrame(main_frame, text="Registro", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.log_text = ScrolledText(log_frame, height=18, wrap="word")
        self.log_text.pack(fill="both", expand=True)

        self._sync_mode_ui()

    def _build_paths_ui(self, parent):
        ttk.Label(parent, text="Corpus origen").grid(row=0, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.source_root, width=70).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(parent, text="Buscar...", command=self._browse_source_root).grid(
            row=0, column=2
        )

        ttk.Label(parent, text="Corpus procesado").grid(row=1, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.processed_root, width=70).grid(
            row=1, column=1, sticky="ew", padx=8, pady=(8, 0)
        )
        ttk.Button(parent, text="Buscar...", command=self._browse_processed_root).grid(
            row=1, column=2, pady=(8, 0)
        )

        parent.columnconfigure(1, weight=1)

    def _build_corpus_ui(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill="x")

        ttk.Button(
            buttons_frame,
            text="Initialize Corpora",
            command=self._start_initialize_corpora,
        ).pack(side="left")
        ttk.Button(
            buttons_frame,
            text="Refrescar corpus",
            command=self._refresh_corpora,
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            buttons_frame,
            text="Seleccionar todos",
            command=self._select_all_corpora,
        ).pack(side="left", padx=(8, 0))

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

        ttk.Radiobutton(
            radio_frame,
            text="Tokens",
            value="tokens",
            variable=self.mode,
            command=self._sync_mode_ui,
        ).pack(side="left")
        ttk.Radiobutton(
            radio_frame,
            text="Types",
            value="types",
            variable=self.mode,
            command=self._sync_mode_ui,
        ).pack(side="left", padx=(12, 0))

        output_frame = ttk.Frame(parent)
        output_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(output_frame, text="Directorio de salida").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=55).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

        ttk.Checkbutton(
            parent,
            text="Generar gráficas en modo tokens",
            variable=self.generate_plots,
        ).pack(anchor="w", pady=(8, 0))

    def _build_types_ui(self, parent):
        ttk.Checkbutton(
            parent,
            text="Todas las categorías",
            variable=self.all_categories,
            command=self._sync_categories_ui,
        ).pack(anchor="w")

        self.categories_listbox = tk.Listbox(
            parent, selectmode=tk.MULTIPLE, exportselection=False, height=8
        )
        self.categories_listbox.pack(fill="x", pady=(8, 0))

    def _build_actions_ui(self, parent):
        ttk.Button(parent, text="Ejecutar análisis", command=self._start_run_analysis).pack(
            side="left"
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

    def _select_all_corpora(self):
        self.corpora_listbox.select_set(0, tk.END)
        self._refresh_categories()

    def _sync_mode_ui(self):
        if self.mode.get() == "types":
            self.types_frame.pack(fill="both", expand=False, pady=(12, 0))
            if self.output_dir.get() == DEFAULT_TOKENS_OUTPUT_DIR:
                self.output_dir.set(DEFAULT_TYPES_OUTPUT_DIR)
        else:
            self.types_frame.pack_forget()
            if self.output_dir.get() == DEFAULT_TYPES_OUTPUT_DIR:
                self.output_dir.set(DEFAULT_TOKENS_OUTPUT_DIR)

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
            return
        source_root = self.source_root.get().strip()
        processed_root = self.processed_root.get().strip()
        self._run_in_background(
            lambda: self._initialize_corpora_worker(source_root, processed_root)
        )

    def _start_run_analysis(self):
        if self._busy:
            return

        mode = self.mode.get()
        processed_root = self.processed_root.get().strip()
        output_dir = self.output_dir.get().strip()
        generate_plots = self.generate_plots.get()
        selected_corpora = self._get_selected_corpora()
        selected_categories = self._get_selected_categories()

        if mode == "types" and selected_categories == []:
            messagebox.showerror(
                "Error",
                "Selecciona al menos una categoría o marca 'Todas las categorías'.",
            )
            return

        self._run_in_background(
            lambda: self._run_analysis_worker(
                mode=mode,
                processed_root=processed_root,
                output_dir=output_dir,
                generate_plots=generate_plots,
                selected_corpora=selected_corpora,
                selected_categories=selected_categories,
            )
        )

    def _run_in_background(self, worker):
        self._busy = True
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

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
            self._busy = False

    def _run_analysis_worker(
        self,
        mode,
        processed_root,
        output_dir,
        generate_plots,
        selected_corpora,
        selected_categories,
    ):
        writer = _QueueWriter(self._enqueue_log)

        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                if mode == "types":
                    result = run_types_analysis(
                        processed_root,
                        selected_corpora=selected_corpora,
                        categories=selected_categories,
                        output_dir=output_dir or DEFAULT_TYPES_OUTPUT_DIR,
                    )
                    self._enqueue_log(
                        "\nAnálisis de types completado. Resultados exportados en: "
                        f"{output_dir or DEFAULT_TYPES_OUTPUT_DIR}\n"
                    )
                else:
                    result = run_tokens_analysis(
                        processed_root,
                        selected_corpora=selected_corpora,
                        output_dir=output_dir or DEFAULT_TOKENS_OUTPUT_DIR,
                        generate_plots=generate_plots,
                    )
                    self._enqueue_log(
                        "\nAnálisis de tokens completado. Resultados exportados en: "
                        f"{output_dir or DEFAULT_TOKENS_OUTPUT_DIR}\n"
                    )
                    if result["plot_outputs"] is not None:
                        self._enqueue_log(
                            "Gráficas guardadas en: "
                            f"{result['plot_outputs']['plots_dir']} y "
                            f"{result['plot_outputs']['distribution_dir']}\n"
                        )
        except Exception as exc:
            self._enqueue_callback(
                lambda: messagebox.showerror("Error al ejecutar el análisis", str(exc))
            )
        finally:
            self._busy = False

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
