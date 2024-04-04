"""dbt utilities."""
import os
from pathlib import Path

from dbt.cli.main import dbtRunner, dbtRunnerResult


class DbtParseException(Exception):
    """Raised when dbt parse fails."""


def dbt_parse() -> dbtRunnerResult:
    """Parse a dbt project.

    Returns:
        dbtRunnerResult: dbt parse result

    raises:
        DbtParseException: dbt parse failed
    """
    result: dbtRunnerResult = dbtRunner().invoke(["parse"])
    if not result.success:
        raise DbtParseException("dbt parse failed.") from result.exception

    return result


def get_manifest_path() -> Path:
    """Get the manifest path."""
    return (
        Path().cwd()
        / os.getenv("DBT_PROJECT_DIR", "")
        / os.getenv("DBT_TARGET_DIR", "target")
        / "manifest.json"
    )
