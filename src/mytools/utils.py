"""Utility functions and logging setup."""
import os
import sys
import logging
from pathlib import Path
from typing import Union
from rich.console import Console
from rich.logging import RichHandler
from .config import settings

console = Console()

def setup_logging():
    """Configure logging with Rich handler.

    Calling this multiple times will reconfigure the root logger.  ``basicConfig``
    only has an effect once unless ``force=True`` (Python 3.8+).  We include that
    flag to make it safe to call from the CLI callback when the log level is
    changed at runtime.
    """
    logging.basicConfig(
        level=settings.log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        force=True,
    )
    log = logging.getLogger("mytools")
    log.setLevel(settings.log_level)
    return log

# global logger instance; can be updated by re-invoking setup_logging()
logger = setup_logging()

def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def clear_screen():
    """Cross-platform clear console."""
    os.system("cls" if os.name == "nt" else "clear")

def get_project_path() -> Path:
    """Get current working directory as project path."""
    return Path.cwd()

def ensure_directory(path: Union[str, Path]) -> Path:
    """Create directory if it doesn't exist."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def read_file_safe(file_path: Union[str, Path], max_size: int = None) -> str:
    """Safely read text file with size limit."""
    path = Path(file_path)
    if max_size is None:
        max_size = settings.max_file_size
    try:
        if path.stat().st_size > max_size:
            logger.warning(f"Skipping {path.name}: size exceeds limit")
            return ""
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, PermissionError) as e:
        logger.debug(f"Cannot read {path}: {e}")
        return ""

def should_ignore(path: Path, ignore_dirs: set, ignore_files: set) -> bool:
    """Check if a file/directory should be ignored."""
    name = path.name
    if path.is_dir():
        return name in ignore_dirs or name.startswith(".")
    else:
        # Check exact name or pattern (simple wildcard support)
        if name in ignore_files:
            return True
        for pattern in ignore_files:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
            if pattern.endswith("*") and name.startswith(pattern[:-1]):
                return True
        return False