"""Example rules."""

from dbt_score import Model, RuleViolation, rule

from tests.rules.rule_filters import skip_schemaX


@rule(rule_filters={skip_schemaX()})
def rule_test_example(model: Model) -> RuleViolation | None:
    """An example rule."""
