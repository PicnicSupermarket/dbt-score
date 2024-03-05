"""CLI interface."""

from typing import Final

import click
from dbt.cli.options import MultiOption

BANNER: Final[str] = """\b
           __ __     __
      ____/ // /_   / /_        _____ _____ ____   _____ ___
     / __  // __ \\ / __/______ / ___// ___// __ \\ / ___// _ \\
    / /_/ // /_/ // /_ /_____/(__  )/ /__ / /_/ // /   /  __/
    \\__,_//_.___/ \\__/       /____/ \\___/ \\____//_/    \\___/
    """


@click.version_option(message="%(version)s")
@click.group(help=BANNER)
def cli() -> None:
    """CLI entrypoint."""


@cli.command()
@click.option(
    "--select",
    "-s",
    help="Specify the nodes to include.",
    cls=MultiOption,
    type=tuple,
    multiple=True,
)
def lint(select: tuple[str]) -> None:
    """Lint dbt models metadata."""
    raise NotImplementedError()
