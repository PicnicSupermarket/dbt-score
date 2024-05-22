"""CLI interface."""

from pathlib import Path
from typing import Final

import click
from click.core import ParameterSource
from dbt.cli.options import MultiOption

from dbt_score.config import Config
from dbt_score.lint import lint_dbt_project
from dbt_score.parse import dbt_parse, get_default_manifest_path
from dbt_score.rule_catalog import display_catalog

BANNER: Final[str] = r"""
          __ __     __
     ____/ // /_   / /_        _____ _____ ____   _____ ___
    / __  // __ \ / __/______ / ___// ___// __ \ / ___// _ \
   / /_/ // /_/ // /_ /_____/(__  )/ /__ / /_/ // /   /  __/
   \__,_//_.___/ \__/       /____/ \___/ \____//_/    \___/
    """


@click.version_option(message="%(version)s")
@click.group(
    help=f"\b{BANNER}",
    invoke_without_command=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)
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
    "--namespace",
    "-n",
    help="Namespace.",
    default=None,
    multiple=True,
)
@click.option(
    "--manifest",
    "-m",
    help="Manifest filepath.",
    type=click.Path(path_type=Path),
    default=get_default_manifest_path(),
)
@click.option(
    "--run-dbt-parse",
    "-p",
    help="Run dbt parse.",
    is_flag=True,
    default=False,
)
def lint(
    select: tuple[str], namespace: list[str], manifest: Path, run_dbt_parse: bool
) -> None:
    """Lint dbt models metadata."""
    manifest_provided = (
        click.get_current_context().get_parameter_source("manifest")
        != ParameterSource.DEFAULT
    )
    if manifest_provided and run_dbt_parse:
        raise click.UsageError("--run-dbt-parse cannot be used with --manifest.")

    config = Config()
    config.load()
    if namespace:
        config.overload({"rule_namespaces": namespace})

    if run_dbt_parse:
        dbt_parse()

    lint_dbt_project(manifest, config)


@cli.command(name="list")
@click.option(
    "--namespace",
    "-n",
    help="Namespace.",
    default=None,
    multiple=True,
)
@click.option(
    "--title",
    help="Page title (Markdown only).",
    default=None,
)
@click.option(
    "--format",
    "-f",
    help="Output format.",
    type=click.Choice(["terminal", "markdown"]),
    default="terminal",
)
def list_command(namespace: list[str], title: str, format: str) -> None:
    """Display rules list."""
    config = Config()
    config.load()
    if namespace:
        config.overload({"rule_namespaces": namespace})

    display_catalog(config, title, format)
