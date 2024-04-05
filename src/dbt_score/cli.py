"""CLI interface."""

import logging
from pathlib import Path
from typing import Final

import click
from click.core import ParameterSource
from dbt.cli.options import MultiOption

from dbt_score.dbt_utils import dbt_parse, get_manifest_path
from dbt_score.lint import lint_dbt_project

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
    type=click.Path(path_type=Path),
    default=get_manifest_path(),
)
@click.option(
    "--run-dbt-parse",
    "-p",
    help="Run dbt parse.",
    is_flag=True,
    default=False,
)
def lint(select: tuple[str], manifest: Path, run_dbt_parse: bool) -> None:
    """Lint dbt models metadata."""
    manifest_provided = (
        click.get_current_context().get_parameter_source("manifest")
        != ParameterSource.DEFAULT
    )
    if manifest_provided and run_dbt_parse:
        raise click.UsageError("--run-dbt-parse cannot be used with --manifest.")

    if run_dbt_parse:
        dbt_parse()

    lint_dbt_project(manifest)
