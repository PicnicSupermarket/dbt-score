"""Lint dbt models metadata."""

import logging
from pathlib import Path

from dbt_score.dbt_utils import dbt_parse

logger = logging.getLogger(__name__)


def lint_manifest(manifest_path: Path) -> None:
    """Lint dbt manifest."""
    if not manifest_path.exists():
        logger.info("Executing dbt parse.")
        dbt_parse()
