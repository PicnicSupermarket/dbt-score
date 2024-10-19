"""Example rules."""

from dbt_score import Model, RuleViolation, rule_filter, rule


@rule()
def rule_test_example(model: Model) -> RuleViolation | None:
    """An example rule."""


@rule_filter
def skip_model1(model: Model) -> bool:
    """An example filter."""
    return model.name != "model1"
