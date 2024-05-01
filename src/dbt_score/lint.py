"""Lint dbt models metadata."""

from pathlib import Path

from dbt_score.config_parser import DbtScoreConfig
from dbt_score.evaluation import Evaluation
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.models import ManifestLoader
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Scorer


def lint_dbt_project(manifest_path: Path, config: DbtScoreConfig | None = None) -> None:
    """Lint dbt manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}.")

    if config is None:
        config = DbtScoreConfig()

    rule_registry = RuleRegistry(config)
    rule_registry.load_all()

    manifest_loader = ManifestLoader(manifest_path)

    formatter = HumanReadableFormatter()

    scorer = Scorer()

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=formatter,
        scorer=scorer,
    )
    evaluation.evaluate()
