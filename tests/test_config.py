"""Tests for the module config_parser."""
from pathlib import Path

import pytest
from dbt_score.config import Config
from dbt_score.rule import RuleConfig, Severity


def test_load_valid_toml_file(valid_config_path):
    """Test that a valid config file loads correctly."""
    config = Config()
    config._load_toml_file(str(valid_config_path))
    assert config.rule_namespaces == ["namespace_foo"]
    assert config.disabled_rules == ["foo", "bar"]
    assert config.rules_config["foobar"].severity == Severity.CRITICAL
    assert (
        config.rules_config["tests.rules.example.rule_test_example"].severity
        == Severity.CRITICAL
    )


def test_load_invalid_toml_file(caplog, invalid_config_path):
    """Test that an invalid config file logs a warning."""
    config = Config()
    config._load_toml_file(str(invalid_config_path))
    assert "Option foo in tool.dbt-score not supported." in caplog.text


def test_invalid_rule_config(rule_severity_low):
    """Test that an invalid rule config raises an exception."""
    config = RuleConfig(params={"foo": "bar"})
    with pytest.raises(
        AttributeError,
        match="Unknown rule parameter: foo for rule "
        "tests.conftest.rule_severity_low.",
    ):
        rule_severity_low(config)


def test_valid_rule_config(valid_config_path, rule_with_params):
    """Test that a valid rule config can be loaded."""
    config = RuleConfig(severity=Severity(4), params={"model_name": "baz"})
    rule_with_params = rule_with_params(config)
    assert rule_with_params.severity == Severity.CRITICAL
    assert rule_with_params.default_params == {"model_name": "model1"}
    assert rule_with_params.params == {"model_name": "baz"}


def test_get_config_file():
    """Test that the config file is found in the current directory."""
    directory = Path(__file__).parent / "resources"
    config = Config()
    config.get_config_file(directory)
    assert config.config_file == directory / "pyproject.toml"


def test_get_parent_config_file():
    """Test that the config file is found in the parent directory."""
    directory = Path(__file__).parent / "resources" / "sub_dir"
    config = Config()
    config.get_config_file(directory)
    assert config.config_file == directory.parent / "pyproject.toml"
