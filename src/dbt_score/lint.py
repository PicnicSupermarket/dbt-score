"""Lint dbt models metadata."""

from pathlib import Path
from typing import Iterable, Literal

from dbt_score.config import Config
from dbt_score.evaluation import Evaluation
from dbt_score.formatters.ascii_formatter import ASCIIFormatter
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.formatters.manifest_formatter import ManifestFormatter
from dbt_score.models import ManifestLoader
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Scorer


def lint_dbt_project(
    manifest_path: Path,
    config: Config,
    format: Literal["plain", "manifest", "ascii"],
    select: Iterable[str] | None = None,
) -> None:
    """Lint dbt manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}.")

    rule_registry = RuleRegistry(config)
    rule_registry.load_all()

    manifest_loader = ManifestLoader(manifest_path, select=select)

    formatters = {
        "plain": HumanReadableFormatter,
        "manifest": ManifestFormatter,
        "ascii": ASCIIFormatter,
    }
    formatter = formatters[format](manifest_loader=manifest_loader)

    scorer = Scorer(config)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=formatter,
        scorer=scorer,
    )
    evaluation.evaluate()
