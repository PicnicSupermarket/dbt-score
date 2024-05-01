"""Tests for the module config_parser."""

import pytest
from dbt_score.config_parser import DbtScoreConfig, RuleConfig
from dbt_score.rule import Severity


def test_load_valid_toml_file(valid_config_path):
    """Test that a valid config file loads correctly."""
    config = DbtScoreConfig()
    config.load_toml_file(str(valid_config_path))
    assert config.rule_namespaces == ["namespace_foo"]
    assert config.disabled_rules == ["foo", "bar"]
    assert config.rules_config["foobar"].severity == 4


def test_load_invalid_toml_file(caplog, invalid_config_path):
    """Test that an invalid config file logs a warning."""
    config = DbtScoreConfig()
    config.load_toml_file(str(invalid_config_path))
    assert "Option foo in tool.dbt-score not supported." in caplog.text


def test_invalid_rule_config(rule_severity_low):
    """Test that an invalid rule config raises an exception."""
    config = RuleConfig(params={"foo": "bar"})
    with pytest.raises(AttributeError, match="Unknown rule parameter: foo."):
        rule_severity_low(config)


def test_valid_rule_config(valid_config_path, rule_with_params):
    """Test that a valid rule config can be loaded."""
    config = RuleConfig(severity=4, description="foo", params={"model_name": "baz"})
    rule_with_params = rule_with_params(config)
    assert rule_with_params.severity == Severity.CRITICAL
    assert rule_with_params.description == "foo"
    assert rule_with_params.default_params == {"model_name": "model1"}
    assert rule_with_params.params == {"model_name": "baz"}
