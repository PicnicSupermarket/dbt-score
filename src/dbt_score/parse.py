"""dbt utilities."""

import logging
import os
from pathlib import Path

from dbt.cli.main import dbtRunner, dbtRunnerResult


class DbtParseException(Exception):
    """Raised when dbt parse fails."""


def dbt_parse() -> dbtRunnerResult:
    """Parse a dbt project.

    Returns:
        The dbt parse run result.

    Raises:
        DbtParseException: dbt parse failed.
    """
    dbt_logger_stdout = logging.getLogger("stdout_log")
    dbt_logger_stdout.disabled = True

    result: dbtRunnerResult = dbtRunner().invoke(["parse"])

    dbt_logger_stdout.disabled = False

    if not result.success:
        raise DbtParseException("dbt parse failed.") from result.exception

    return result


def get_default_manifest_path() -> Path:
    """Get the manifest path."""
    return (
        Path().cwd()
        / os.getenv("DBT_PROJECT_DIR", "")
        / os.getenv("DBT_TARGET_DIR", "target")
        / "manifest.json"
    )
