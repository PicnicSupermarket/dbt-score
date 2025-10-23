"""dbt utilities."""

import contextlib
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, cast

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


def manifest_needs_regeneration(manifest_path: Path | None = None) -> bool:
    """Check if the manifest needs to be regenerated.

    Compares the modification time of the manifest against all .sql and .yml files
    in the dbt project to determine if a re-parse is needed.

    Args:
        manifest_path: Path to the manifest.json file. If None, uses default path.

    Returns:
        True if manifest is missing or outdated, False if up-to-date.
    """
    if manifest_path is None:
        manifest_path = get_default_manifest_path()

    # If manifest doesn't exist, we need to generate it
    if not manifest_path.exists():
        return True

    manifest_time = manifest_path.stat().st_mtime

    # Get the dbt project directory (parent of target directory)
    if manifest_path.parent.name == os.getenv("DBT_TARGET_DIR", "target"):
        project_dir = manifest_path.parent.parent
    else:
        project_dir = Path.cwd()

    # Check if any .sql, .yml, or .yaml files are newer than manifest
    for pattern in ("**/*.sql", "**/*.yml", "**/*.yaml"):
        for file in project_dir.glob(pattern):
            # Skip files in target directory to avoid checking generated files
            if os.getenv("DBT_TARGET_DIR", "target") in file.parts:
                continue
            if file.stat().st_mtime > manifest_time:
                return True

    return False


@dbt_required
def dbt_parse(
    force: bool = False, manifest_path: Path | None = None
) -> "dbtRunnerResult":
    """Parse a dbt project.

    Args:
        force: If True, always run dbt parse. If False, skip if manifest is up-to-date.
        manifest_path: Path to check for manifest freshness. If None, uses default path.

    Returns:
        The dbt parse run result.

    Raises:
        DbtParseException: dbt parse failed.
    """
    if not force and not manifest_needs_regeneration(manifest_path):
        # Return a mock successful result when skipping parse
        # This maintains backward compatibility with code expecting a result
        class MockResult:
            success = True
            exception = None

        return cast("dbtRunnerResult", MockResult())

    with _disable_dbt_stdout():
        result: "dbtRunnerResult" = dbtRunner().invoke(["parse"])

    if not result.success:
        raise DbtParseException(root_cause=result.exception)

    return result


@dbt_required
def dbt_ls(select: Iterable[str] | None) -> Iterable[str]:
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
