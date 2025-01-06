"""Rule filters."""

from dbt_score import rule_filter
from dbt_score.models import Model


@rule_filter
def is_table(model: Model) -> bool:
    """Models that are tables."""
    return model.config.get("materialized") in {"table", "incremental"}
