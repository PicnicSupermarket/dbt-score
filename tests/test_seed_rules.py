import pytest

from dbt_score.rule import RuleViolation
from dbt_score.rules.generic import (
    seed_has_description,
    seed_columns_have_description,
    seed_has_tests,
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


def test_seed_has_tests(seed1, seed2):
    """Test seed_has_tests rule."""
    # Mock test data
    seed1.tests = [{"name": "test1"}]  # Add a fake test
    seed2.tests = []  # No tests
    
    rule = seed_has_tests()
    assert rule.evaluate(seed1) is None
    assert isinstance(rule.evaluate(seed2), RuleViolation)


def test_seed_has_owner(seed1, seed2):
    """Test seed_has_owner rule."""
    # Add owner to seed1, not to seed2
    seed1.meta["owner"] = "Data Team"
    
    rule = seed_has_owner()
    assert rule.evaluate(seed1) is None
    assert isinstance(rule.evaluate(seed2), RuleViolation)