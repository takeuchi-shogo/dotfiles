"""Claude Code hook shared library."""
import sys
from pathlib import Path

# lib/ 自体を sys.path に追加（session_events.py を import 可能にする）
_lib_dir = str(Path(__file__).resolve().parent)
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)
