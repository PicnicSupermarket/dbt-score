"""Test configuration."""


def pytest_sessionfinish(session, exitstatus):
    """Avoid ci failure if no tests are found."""
    if exitstatus == 5:
        session.exitstatus = 0
