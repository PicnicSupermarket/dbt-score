"""Rules and filters to be imported."""


from dbt_score import Model, RuleViolation, rule, rule_filter


@rule
def rule_to_be_imported(model: Model) -> RuleViolation | None:
    """An example rule."""


@rule_filter
def rule_filter_to_be_imported(model: Model) -> bool:  # type: ignore[empty-body]
    """An example filter."""
