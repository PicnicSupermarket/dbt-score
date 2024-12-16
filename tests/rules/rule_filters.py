"""Example rule filters."""

from dbt_score import Model, rule_filter


@rule_filter
def skip_model1(model: Model) -> bool:
    """An example filter."""
    return model.name != "model1"


@rule_filter
def skip_schemaX(model: Model) -> bool:
    """An example filter."""
    return model.schema != "X"
