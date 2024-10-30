"""dbt utilities."""

import contextlib
import os
from pathlib import Path
from typing import Iterable, Iterator, cast

# Conditionally import dbt objects.
try:
    DBT_INSTALLED = True
    from dbt.cli.main import dbtRunner, dbtRunnerResult  # type: ignore
except ImportError:
    DBT_INSTALLED = False


class DbtNotInstalledException(Exception):
    """Raised when trying to run dbt when dbt is not installed."""


class DbtParseException(Exception):
    """Raised when dbt parse fails."""


class DbtLsException(Exception):
    """Raised when dbt ls fails."""


@contextlib.contextmanager
def _disable_dbt_stdout() -> Iterator[None]:
    with contextlib.redirect_stdout(None):
        yield


def dbt_parse() -> "dbtRunnerResult":
    """Parse a dbt project.

    Returns:
        The dbt parse run result.

    Raises:
        DbtParseException: dbt parse failed.
    """
    if not DBT_INSTALLED:
        raise DbtNotInstalledException(
            "This option requires dbt to be installed in the same Python"
            "environment as dbt-score."
        )

    with _disable_dbt_stdout():
        result: "dbtRunnerResult" = dbtRunner().invoke(["parse"])

    if not result.success:
        raise DbtParseException("dbt parse failed.") from result.exception

    return result


def dbt_ls(select: Iterable[str] | None) -> Iterable[str]:
    """Run dbt ls."""
    if not DBT_INSTALLED:
        raise DbtNotInstalledException(
            "This option requires dbt to be installed in the same Python"
            "environment as dbt-score."
        )

    cmd = ["ls", "--resource-type", "model", "--output", "name"]
    if select:
        cmd += ["--select", *select]

    with _disable_dbt_stdout():
        result: "dbtRunnerResult" = dbtRunner().invoke(cmd)

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
