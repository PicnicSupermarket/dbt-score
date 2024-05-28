"""Tests for the module config_parser."""
from pathlib import Path

import pytest
from dbt_score.config import Config, MedalConfig
from dbt_score.rule import RuleConfig, Severity


def test_load_valid_toml_file(valid_config_path):
    """Test that a valid config file loads correctly."""
    config = Config()
    config._load_toml_file(str(valid_config_path))
    assert config.rule_namespaces == ["foo", "tests"]
    assert config.disabled_rules == ["foo.foo", "tests.bar"]
    assert config.rules_config["foo.bar"].severity == Severity.CRITICAL
    assert (
        config.rules_config["tests.rules.example.rule_test_example"].severity
        == Severity.CRITICAL
    )
    assert config.medal_config.bronze_threshold == 6.0
    assert config.medal_config.silver_threshold == 7.0
    assert config.medal_config.gold_threshold == 10.0


def test_load_invalid_toml_file(caplog, invalid_config_path):
    """Test that an invalid config file logs a warning."""
    config = Config()
    config._load_toml_file(str(invalid_config_path))
    assert "Option foo in tool.dbt-score not supported." in caplog.text


def test_invalid_rule_config(rule_severity_low):
    """Test that an invalid rule config raises an exception."""
    config = RuleConfig(config={"foo": "bar"})
    with pytest.raises(
        AttributeError,
        match="Unknown rule parameter: foo for rule "
        "tests.conftest.rule_severity_low.",
    ):
        rule_severity_low(config)


def test_invalid_medal_thresholds():
    """Test that invalid medal thresholds raises an exception."""
    medal_config = MedalConfig()
    medal_config.bronze_threshold = 9.0
    medal_config.silver_threshold = 8.0
    medal_config.gold_threshold = 10.0
    with pytest.raises(ValueError, match="bronze_threshold must be lower than"):
        medal_config.validate()

    medal_config = MedalConfig()
    medal_config.bronze_threshold = 8.0
    medal_config.silver_threshold = 9.5
    medal_config.gold_threshold = 9.5
    with pytest.raises(ValueError, match="silver_threshold must be lower than"):
        medal_config.validate()


def test_valid_rule_config(valid_config_path, rule_with_config):
    """Test that a valid rule config can be loaded."""
    config = RuleConfig(severity=Severity(4), config={"model_name": "baz"})
    rule_with_config = rule_with_config(config)
    assert rule_with_config.severity == Severity.CRITICAL
    assert rule_with_config.default_config == {"model_name": "model1"}
    assert rule_with_config.config == {"model_name": "baz"}


def test_get_config_file():
    """Test that the config file is found in the current directory."""
    directory = Path(__file__).parent / "resources"
    config = Config()
    config_file = config.get_config_file(directory)
    assert config_file == directory / "pyproject.toml"


def test_get_parent_config_file():
    """Test that the config file is found in the parent directory."""
    directory = Path(__file__).parent / "resources" / "sub_dir"
    config = Config()
    config_file = config.get_config_file(directory)
    assert config_file == directory.parent / "pyproject.toml"


def test_config_overload(valid_config_path):
    """Test overloading of config values."""
    config = Config()
    config._load_toml_file(str(valid_config_path))
    config.overload({"rule_namespaces": ["x", "y"], "disabled_rules": ["foo"]})
    assert config.rule_namespaces == ["x", "y"]
    assert config.disabled_rules == ["foo"]
