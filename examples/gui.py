import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui import run_app


if __name__ == "__main__":
    run_app()
