"""Configuration management with pydantic-settings."""
from pathlib import Path
from typing import Set, Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """Application settings loaded from environment and .env file."""

    model_config = SettingsConfigDict(
        env_prefix="MYTOOLS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ignore directories (defaults + user additions)
    ignore_dirs: Set[str] = Field(
        default_factory=lambda: {
            ".git", ".venv", "venv", "env", "__pycache__",
            ".idea", ".vscode", "node_modules", "dist", "build",
            "migrations", "logs", ".pytest_cache", ".mypy_cache",
        }
    )

    # Ignore file patterns (supports wildcards via fnmatch)
    ignore_files: Set[str] = Field(
        default_factory=lambda: {
            ".DS_Store", "Thumbs.db", "*.pyc", "*.pyo", "*.pyd",
            "*.log", "*.tmp", ".env", ".env.*", "*.db", "*.sqlite3",
        }
    )

    # Maximum file size to read when generating context (in bytes)
    max_file_size: int = 100_000  # 100 KB

    # Maximum total size of context output (in bytes)
    max_total_size: int = 500_000  # 500 KB

    # Log level (DEBUG, INFO, WARNING, ERROR)
    log_level: str = "INFO"

    # Optional path to user config file (TOML/YAML)
    config_file: Optional[Path] = None

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        v = v.upper()
        if v not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            return "INFO"
        return v

# Global settings instance
settings = Settings()

# Allow runtime updates (e.g., adding ignore dirs)
def add_ignore_dir(directory: str) -> None:
    settings.ignore_dirs.add(directory)

def add_ignore_file(pattern: str) -> None:
    settings.ignore_files.add(pattern)