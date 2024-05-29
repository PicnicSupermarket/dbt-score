"""dbt utilities."""

import contextlib
import os
from pathlib import Path
from typing import Iterable, Iterator, cast

from dbt.cli.main import dbtRunner, dbtRunnerResult


class DbtParseException(Exception):
    """Raised when dbt parse fails."""


class DbtLsException(Exception):
    """Raised when dbt ls fails."""


@contextlib.contextmanager
def _disable_dbt_stdout() -> Iterator[None]:
    with contextlib.redirect_stdout(None):
        yield


def dbt_parse() -> dbtRunnerResult:
    """Parse a dbt project.

    Returns:
        The dbt parse run result.

    Raises:
        DbtParseException: dbt parse failed.
    """
    with _disable_dbt_stdout():
        result: dbtRunnerResult = dbtRunner().invoke(["parse"])

    if not result.success:
        raise DbtParseException("dbt parse failed.") from result.exception

    return result


def dbt_ls(select: Iterable[str] | None) -> Iterable[str]:
    """Run dbt ls."""
    cmd = ["ls", "--resource-type", "model", "--output", "name"]
    if select:
        cmd += ["--select", *select]

    with _disable_dbt_stdout():
        result: dbtRunnerResult = dbtRunner().invoke(cmd)

    if not result.success:
        raise DbtLsException("dbt ls failed.") from result.exception

    selected = cast(Iterable[str], result.result)  # mypy hint
    return selected


def get_default_manifest_path() -> Path:
    """Get the manifest path."""
    return (
        Path().cwd()
        / os.getenv("DBT_PROJECT_DIR", "")
        / os.getenv("DBT_TARGET_DIR", "target")
        / "manifest.json"
    )
