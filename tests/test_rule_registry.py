"""Unit tests for the rule registry."""

import pytest
from dbt_score.exceptions import DuplicatedRuleException
from dbt_score.rule_registry import RuleRegistry


def test_rule_registry_discovery():
    """Ensure rules can be found in a given namespace recursively."""
    r = RuleRegistry()
    r._load("tests.rules")
    assert sorted(r.rules.keys()) == ["rule_test_example", "rule_test_nested_example"]


def test_rule_registry_no_duplicates():
    """Ensure no duplicate rule names can coexist."""
    r = RuleRegistry()
    r._load("tests.rules")
    with pytest.raises(DuplicatedRuleException):
        r._load("tests.rules")


def test_rule_registry_core_rules():
    """Ensure core rules are automatically discovered."""
    r = RuleRegistry()
    r.load_all()
    assert len(r.rules) > 0
