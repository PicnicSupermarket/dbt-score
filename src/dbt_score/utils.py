"""Utilities."""

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
        raise DbtParseException("Parsing dbt project failed.")

    return result
