"""Tests for seed rules."""

from dbt_score.models import Column
from dbt_score.rule import RuleViolation
from dbt_score.rules.generic import (
    seed_columns_have_description,
    seed_has_description,
    seed_has_owner,
)


def test_seed_has_description(seed1, seed2):
    """Test seed_has_description rule."""
    # seed1 has a description, seed2 doesn't
    rule = seed_has_description()
    assert rule.evaluate(seed1) is None
    assert isinstance(rule.evaluate(seed2), RuleViolation)


def test_seed_columns_have_description(seed1, seed2):
    """Test seed_columns_have_description rule."""
    # seed1's column has a description, seed2's column doesn't
    rule = seed_columns_have_description()
    assert rule.evaluate(seed1) is None
    assert isinstance(rule.evaluate(seed2), RuleViolation)


def test_seed_has_owner(seed1, seed2):
    """Test seed_has_owner rule."""
    # Add owner to seed1, not to seed2
    seed1.config["meta"] = {"owner": "Data Team"}

    rule = seed_has_owner()
    assert rule.evaluate(seed1) is None
    assert isinstance(rule.evaluate(seed2), RuleViolation)


def test_seed_columns_have_description_message_truncated(seed1):
    """A long list of undocumented seed columns produces a truncated message."""
    rule = seed_columns_have_description()
    for i in range(20):
        seed1.columns.append(Column(name=f"undocumented_column_{i}", description=""))
    result = rule.evaluate(seed1)
    assert isinstance(result, RuleViolation)
    assert result.message is not None
    assert result.message.endswith("…")
