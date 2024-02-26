"""Test configuration."""

from pytest import ExitCode, Session


def pytest_sessionfinish(session: Session, exitstatus: int):
    """Avoid ci failure if no tests are found."""
    if exitstatus == ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = ExitCode.OK
