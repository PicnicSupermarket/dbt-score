"""Lint dbt models metadata."""

from pathlib import Path


def lint_dbt_project(manifest_path: Path) -> None:
    """Lint dbt manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}.")
