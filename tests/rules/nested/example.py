"""Example rules."""

from dbt_score import Model, RuleViolation, rule


@rule
def rule_test_nested_example(model: Model) -> RuleViolation | None:
    """An example rule."""
