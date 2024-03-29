"""Example rules."""

from dbt_score.models import Model
from dbt_score.rule import RuleViolation, rule


@rule()
def rule_test_nested_example(model: Model) -> RuleViolation | None:
    """An example rule."""
