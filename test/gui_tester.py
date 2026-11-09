"""Drive the Tkinter GUI the way a person would.

The names follow Flutter's widget tests:

- ``tap`` is ``tester.tap(find.text(...))``
- ``pump`` is ``tester.pump()``
- ``pump_and_settle`` is ``tester.pumpAndSettle()``
"""

import json
import threading
import time
import tkinter as tk


_INVOKABLE = {
    "Button",
    "Checkbutton",
    "Radiobutton",
    "TButton",
    "TCheckbutton",
    "TRadiobutton",
}


class DialogLog:
    def __init__(self):
        self.entries = []

    def showerror(self, title, message, **_kwargs):
        self.entries.append(("error", title, message))

    def showinfo(self, title, message, **_kwargs):
        self.entries.append(("info", title, message))

    def showwarning(self, title, message, **_kwargs):
        self.entries.append(("warning", title, message))

    def clear(self):
        self.entries.clear()


class DirectoryChooser:
    def __init__(self):
        self.queue = []
        self.calls = []

    def askdirectory(self, **kwargs):
        self.calls.append(kwargs)
        if not self.queue:
            return ""
        return self.queue.pop(0)


class AnalysisProcessDouble:
    """Stand in for every process the GUI starts while the window is open.

    Forking a real process from the worker thread while Tk is inside
    ``update()`` can hang on Linux. The window still builds the real analysis
    command; this double only replaces the launch.
    """

    def __init__(self):
        self.return_code = 0
        self._invocations = []
        self._lock = threading.Lock()

    def __call__(self, command, **kwargs):
        command = tuple(str(part) for part in command)
        if not any(part.endswith("gui_analysis_runner.py") for part in command):
            return _SuccessfulProbe(command)

        with self._lock:
            self._invocations.append((command, kwargs.get("cwd")))

        mode = _runner_mode(command)
        payload = {}
        if "--generate-plots" in command:
            if mode == "types":
                payload = {"plot_outputs": {"plots_dir": "types-plots"}}
            else:
                payload = {
                    "plot_outputs": {
                        "plots_dir": "token-plots",
                        "distribution_dir": "token-dist",
                    }
                }

        result_path = command[command.index("--result-file") + 1]
        with open(result_path, "w", encoding="utf-8") as result_file:
            json.dump(payload, result_file)

        return _FakeProcess(
            return_code=lambda: self.return_code,
            args=command,
        )

    @property
    def commands(self):
        with self._lock:
            return [command for command, _cwd in self._invocations]

    @property
    def working_directories(self):
        with self._lock:
            return [cwd for _command, cwd in self._invocations]


class _SuccessfulProbe:
    """Stand-in for the interpreter check, which must not fork."""

    def __init__(self, args):
        self.args = args
        self.pid = 0
        self.returncode = 0
        self.stdout = None
        self.stderr = None

    def communicate(self, input=None, timeout=None):
        return (None, None)

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class _FakeProcess:
    def __init__(self, return_code, args):
        self.args = args
        self.pid = 4242
        self.returncode = None
        self.stdout = iter(("external analysis output\n",))
        self.stderr = None
        self._return_code = return_code

    def communicate(self, input=None, timeout=None):
        output = "".join(self.stdout)
        self.returncode = self.wait(timeout=timeout)
        return (output, None)

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self.returncode = self._return_code()
        return self.returncode

    def kill(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.wait()
        return False


class GuiTester:
    def __init__(self, app, dialogs, directories, analysis):
        self.app = app
        self.dialogs = dialogs
        self.directories = directories
        self.analysis = analysis

    def pump(self):
        self.app.update_idletasks()
        self.app.update()

    def pump_for(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.pump()
            time.sleep(0.05)

    def pump_and_settle(self, timeout=15):
        deadline = time.monotonic() + timeout
        idle_passes = 0
        while time.monotonic() < deadline:
            self.pump()
            if self.app._busy or not self.app._log_queue.empty():
                idle_passes = 0
            else:
                idle_passes += 1
                if idle_passes >= 3:
                    return
            time.sleep(0.05)

        raise AssertionError(
            "GUI did not become idle within "
            f"{timeout}s.\nstatus={self.status()}\n"
            f"dialogs={self.dialogs.entries}\n"
            f"log={self.log_text()}"
        )

    def queue_directory(self, path):
        self.directories.queue.append(path)

    def tap(self, text, *, root=None, index=0):
        self.control(text, root=root, index=index).invoke()
        self.pump()

    def choose(self, option):
        combos = [
            widget
            for widget in self.walk()
            if widget.winfo_class() == "TCombobox" and self.is_shown(widget)
        ]
        if len(combos) != 1:
            raise AssertionError(f"Expected one combobox, found {len(combos)}")

        combo = combos[0]
        values = combo.cget("values")
        if option not in values:
            raise AssertionError(f"{option!r} is not in {values!r}")

        combo.set(option)
        combo.event_generate("<<ComboboxSelected>>")
        self.pump()

    def enter(self, variable, value):
        entry = self.entry(variable)
        entry.delete(0, tk.END)
        entry.insert(0, value)
        self.pump()

    def field(self, variable):
        return self.entry(variable).get()

    def entry(self, variable):
        name = str(variable)
        matches = []
        for widget in self.walk():
            if widget.winfo_class() not in {"Entry", "TEntry"}:
                continue
            try:
                linked = str(widget.cget("textvariable"))
            except tk.TclError:
                continue
            if linked == name:
                matches.append(widget)

        if len(matches) != 1:
            raise AssertionError(
                f"Expected one entry for {name}, found {len(matches)}"
            )
        return matches[0]

    def section(self, title):
        matches = [
            widget
            for widget in self.find(title)
            if widget.winfo_class() == "TLabelframe"
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"Expected one section {title!r}.\n{self.describe()}"
            )
        return matches[0]

    def visible(self, text):
        return bool(self.find(text))

    def visible_text_containing(self, snippet):
        for widget in self.walk():
            if not self.is_shown(widget):
                continue
            text = self.widget_text(widget)
            if text and snippet in text:
                return text
        return None

    def status(self):
        return self.app.status_text.get()

    def log_text(self):
        return self.app.log_text.get("1.0", "end-1c")

    def is_enabled(self, text, *, root=None):
        state = set(str(self.control(text, root=root).cget("state")).split())
        return "disabled" not in state

    def is_selected(self, text, *, root=None):
        widget = self.control(text, root=root)
        value = self.app.globalgetvar(str(widget.cget("variable")))
        if isinstance(value, str):
            return value not in {"0", "false", "False", ""}
        return bool(value)

    def expect_dialog(self, kind, title, message):
        assert self.dialogs.entries, "expected a dialog, but none was shown"
        assert len(self.dialogs.entries) == 1, self.dialogs.entries
        got_kind, got_title, got_message = self.dialogs.entries[0]
        assert got_kind == kind
        assert got_title == title
        assert message in got_message

    def clear_dialogs(self):
        self.dialogs.clear()

    def control(self, text, *, root=None, index=0):
        matches = [
            widget
            for widget in self.find(text, root=root)
            if widget.winfo_class() in _INVOKABLE
        ]
        if index >= len(matches):
            raise AssertionError(
                f"No visible control {text!r} at index {index}.\n{self.describe()}"
            )
        return matches[index]

    def find(self, text, *, root=None):
        matches = []
        for widget in self.walk(root):
            if not self.is_shown(widget):
                continue
            if self.widget_text(widget) == text:
                matches.append(widget)
        return matches

    def walk(self, root=None):
        root = self.app if root is None else root
        try:
            if not int(root.winfo_exists()):
                return
        except tk.TclError:
            return

        yield root
        try:
            children = root.winfo_children()
        except tk.TclError:
            return

        for child in children:
            yield from self.walk(child)

    def is_shown(self, widget):
        current = widget
        while not isinstance(current, tk.Tk) and current.master is not None:
            try:
                manager = current.winfo_manager()
                parent_class = current.master.winfo_class()
            except tk.TclError:
                return False

            embedded_in_canvas = parent_class == "Canvas" and not manager
            if not manager and not embedded_in_canvas:
                return False
            current = current.master
        return True

    def widget_text(self, widget):
        try:
            return widget.cget("text")
        except tk.TclError:
            return None

    def describe(self):
        lines = []
        for widget in self.walk():
            if not self.is_shown(widget):
                continue
            text = self.widget_text(widget)
            if text:
                lines.append(f"{widget.winfo_class()}: {text}")
        return "\n".join(lines)


def _runner_mode(command):
    for index, part in enumerate(command):
        if str(part).endswith("gui_analysis_runner.py"):
            return command[index + 1]
    raise AssertionError(f"Analysis runner missing from {command}")
