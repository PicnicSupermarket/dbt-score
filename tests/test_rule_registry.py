"""Unit tests for the rule registry."""

import pytest
from dbt_score import Severity
from dbt_score.config import Config
from dbt_score.exceptions import DuplicatedRuleException
from dbt_score.rule_registry import RuleRegistry


def test_rule_registry_discovery(default_config):
    """Ensure rules can be found in a given namespace recursively."""
    r = RuleRegistry(default_config)
    r._load("tests.rules")
    assert sorted(r._rules.keys()) == [
        "tests.rules.example.rule_test_example",
        "tests.rules.nested.example.rule_test_nested_example",
    ]


def test_disabled_rule_registry_discovery():
    """Ensure disabled rules are not discovered."""
    config = Config()
    config.disabled_rules = ["tests.rules.nested.example.rule_test_nested_example"]
    r = RuleRegistry(config)
    r._load("tests.rules")
    assert sorted(r._rules.keys()) == [
        "tests.rules.example.rule_test_example",
    ]


def test_configured_rule_registry_discovery(valid_config_path):
    """Ensure rules are discovered and configured correctly."""
    config = Config()
    config._load_toml_file(str(valid_config_path))
    r = RuleRegistry(config)
    r._load("tests.rules")
    assert (
        r.rules["tests.rules.example.rule_test_example"].severity == Severity.CRITICAL
    )


def test_rule_registry_no_duplicates(default_config):
    """Ensure no duplicate rule names can coexist."""
    r = RuleRegistry(default_config)
    r._load("tests.rules")
    with pytest.raises(DuplicatedRuleException):
        r._load("tests.rules")


def test_rule_registry_core_rules(default_config):
    """Ensure core rules are automatically discovered."""
    r = RuleRegistry(default_config)
    r.load_all()
    assert len(r.rules) > 0
