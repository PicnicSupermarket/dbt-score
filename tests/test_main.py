"""Tests for the module entry point."""

import logging
from unittest.mock import patch

from dbt_score.__main__ import main, set_logging


def test_set_logging():
    """Test that logging handlers are configured at WARNING level."""
    set_logging()
    handlers = logging.getLogger().handlers
    assert handlers
    assert all(handler.level == logging.WARNING for handler in handlers)


def test_main_invokes_cli():
    """Test that main sets logging and invokes the CLI."""
    with patch("dbt_score.__main__.set_logging") as mock_set_logging, patch(
        "dbt_score.__main__.cli"
    ) as mock_cli:
        main()

    mock_set_logging.assert_called_once()
    mock_cli.assert_called_once()
