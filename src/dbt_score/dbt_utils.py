"""dbt utilities."""

import contextlib
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, cast

# Conditionally import dbt objects.
try:
    DBT_INSTALLED = True
    from dbt.cli.main import (  # type: ignore[import-not-found, unused-ignore]
        dbtRunner,
        dbtRunnerResult,
    )
except ImportError:
    DBT_INSTALLED = False


class DbtNotInstalledException(Exception):
    """Raised when trying to run dbt when dbt is not installed."""


class DbtParseException(Exception):
    """Raised when dbt parse fails."""

    def __init__(self, root_cause: BaseException | None = None):
        """Initialize the exception."""
        super().__init__()
        self.root_cause = root_cause

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        if self.root_cause:
            return f"dbt parse failed.\n\n{self.root_cause!s}"

        return (
            "dbt parse failed. Root cause not found. Please run `dbt parse` manually."
        )


class DbtLsException(Exception):
    """Raised when dbt ls fails."""


def dbt_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for methods that require dbt to be installed."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not DBT_INSTALLED:
            raise DbtNotInstalledException(
                "This option requires dbt to be installed in the same Python"
                "environment as dbt-score."
            )
        return func(*args, **kwargs)

    return wrapper


@contextlib.contextmanager
def _disable_dbt_stdout() -> Iterator[None]:
    with contextlib.redirect_stdout(None):
        yield


@dbt_required
def dbt_parse(project_dir: Path | None = None) -> "dbtRunnerResult":
    """Parse a dbt project.

    Args:
        project_dir: The dbt project directory. Defaults to the directory dbt
            would use on its own, i.e. the current working directory.

    Returns:
        The dbt parse run result.

    Raises:
        DbtParseException: dbt parse failed.
    """
    cmd = ["parse"]
    if project_dir is not None:
        cmd += ["--project-dir", str(project_dir)]

    with _disable_dbt_stdout():
        result: "dbtRunnerResult" = dbtRunner().invoke(cmd)

    if not result.success:
        raise DbtParseException(root_cause=result.exception)

    return result


@dbt_required
def dbt_ls(
    select: Iterable[str] | None,
    exclude: Iterable[str] | None = None,
    project_dir: Path | None = None,
) -> Iterable[str]:
    """Run dbt ls."""
    cmd = [
        "ls",
        "--resource-types",
        "model",
        "source",
        "snapshot",
        "exposure",
        "seed",
        "--output",
        "name",
    ]
    if select:
        cmd += ["--select", *select]
    if exclude:
        cmd += ["--exclude", *exclude]
    if project_dir is not None:
        cmd += ["--project-dir", str(project_dir)]

    with _disable_dbt_stdout():
        result: "dbtRunnerResult" = dbtRunner().invoke(cmd)

    if not result.success:
        raise DbtLsException("dbt ls failed.") from result.exception

    selected = cast(Iterable[str], result.result)  # mypy hint
    return selected


def get_default_manifest_path(project_dir: Path | None = None) -> Path:
    """Get the manifest path.

    Args:
        project_dir: The dbt project directory. Defaults to the current working
            directory, combined with the `DBT_PROJECT_DIR` environment variable
            if it is set.

    Returns:
        The path of `manifest.json` in the target directory of the project.
    """
    if project_dir is None:
        project_dir = Path.cwd() / os.getenv("DBT_PROJECT_DIR", "")
    return project_dir / os.getenv("DBT_TARGET_DIR", "target") / "manifest.json"
