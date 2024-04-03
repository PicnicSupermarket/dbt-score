"""Entry point of the dbt_score.

This enables module to be run directly.
"""

import logging
import sys

from dbt_score.cli import cli


def set_logging() -> None:
    """Set logging configuration."""
    log_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(
        format=log_format,
        handlers=handlers,
        level=logging.INFO,
    )
    for handler in logging.getLogger("").handlers:
        handler.setLevel(logging.INFO)


if __name__ == "__main__":
    set_logging()
    cli()
