"""Tests for the module config_parser."""
from pathlib import Path
from unittest.mock import patch

import pytest
from dbt_score.config import BadgeConfig, Config
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
    assert config.badge_config.third.threshold == 6.5
    assert config.badge_config.second.threshold == 7.5
    assert config.badge_config.first.threshold == 9.5
    assert config.badge_config.wip.icon == "🏗️"
    assert config.badge_config.third.icon == "3️⃣"
    assert config.badge_config.second.icon == "2️⃣"
    assert config.badge_config.first.icon == "1️⃣"


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


@patch("dbt_score.config.open")
def test_load_invalid_badge_config(mock_open):
    """Test that an invalid badge config raises an exception."""
    config = Config()

    with patch("dbt_score.config.tomllib.load") as mock_load:
        mock_load.return_value = {
            "tool": {"dbt-score": {"badges": {"foo": {"threshold": 1.0}}}}
        }
        with pytest.raises(AttributeError, match="Config only accepts badges:"):
            config._load_toml_file("foo")

        mock_load.return_value = {
            "tool": {"dbt-score": {"badges": {"first": {"foo": "bar"}}}}
        }
        with pytest.raises(AttributeError, match="Badge first: config only accepts"):
            config._load_toml_file("foo")


def test_invalid_badge_thresholds():
    """Test that invalid badge thresholds raises an exception."""
    badge_config = BadgeConfig()
    badge_config.third.threshold = 9.0
    badge_config.second.threshold = 8.0
    badge_config.first.threshold = 10.0
    with pytest.raises(ValueError, match="Invalid badge thresholds."):
        badge_config.validate()

    badge_config = BadgeConfig()
    badge_config.third.threshold = 8.0
    badge_config.second.threshold = 9.5
    badge_config.first.threshold = 9.5
    with pytest.raises(ValueError, match="Invalid badge thresholds."):
        badge_config.validate()

    badge_config = BadgeConfig()
    badge_config.third.threshold = -1
    with pytest.raises(ValueError, match="third threshold must be 0.0 or higher."):
        badge_config.validate()

    badge_config = BadgeConfig()
    badge_config.first.threshold = 11.0
    with pytest.raises(ValueError, match="first threshold must 10.0 or lower."):
        badge_config.validate()

    badge_config = BadgeConfig()
    badge_config.wip.threshold = 1.0
    with pytest.raises(
        AttributeError, match="wip badge cannot have a threshold configuration."
    ):
        badge_config.validate()


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
