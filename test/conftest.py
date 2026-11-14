import ctypes
import os
import sys

# Matplotlib's default Linux backend opens X11 while the suite is importing.
# A later fork from a Tk worker can then hang unless X11 was made thread-safe
# before that first display connection.
if sys.platform == "linux":
    try:
        ctypes.CDLL("libX11.so.6").XInitThreads()
    except OSError:
        pass

os.environ.setdefault("MPLBACKEND", "Agg")

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
