"""CLI interface."""

import logging
from pathlib import Path
from typing import Final

import click
from dbt.cli.options import MultiOption

from dbt_score.dbt_utils import get_manifest_path
from dbt_score.lint import lint_manifest

logger = logging.getLogger(__name__)

BANNER: Final[str] = r"""
          __ __     __
     ____/ // /_   / /_        _____ _____ ____   _____ ___
    / __  // __ \ / __/______ / ___// ___// __ \ / ___// _ \
   / /_/ // /_/ // /_ /_____/(__  )/ /__ / /_/ // /   /  __/
   \__,_//_.___/ \__/       /____/ \___/ \____//_/    \___/
    """


@click.version_option(message="%(version)s")
@click.group(help=f"\b{BANNER}", invoke_without_command=False)
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
@click.option(
    "--manifest",
    "-m",
    help="Manifest filepath.",
    type=click.Path(exists=True),
)
def lint(select: tuple[str], manifest: Path) -> None:
    """Lint dbt models metadata."""
    manifest_path = get_manifest_path() if not manifest else manifest
    lint_manifest(manifest_path)
