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
        "tests.rules.nested.example.rule_test_nested_example",
        "tests.rules.rules.rule_test_example",
    ]
    assert list(r._rule_filters.keys()) == [
        "tests.rules.rule_filters.skip_model1",
        "tests.rules.rule_filters.skip_schemaX",
    ]


def test_disabled_rule_registry_discovery():
    """Ensure disabled rules are not discovered."""
    config = Config()
    config.disabled_rules = ["tests.rules.nested.example.rule_test_nested_example"]
    r = RuleRegistry(config)
    r._load("tests.rules")
    assert sorted(r._rules.keys()) == [
        "tests.rules.rules.rule_test_example",
    ]


def test_configured_rule_registry_discovery(valid_config_path):
    """Ensure rules are discovered and configured correctly."""
    config = Config()
    config._load_toml_file(str(valid_config_path))
    r = RuleRegistry(config)
    r._load("tests.rules")
    assert r.rules["tests.rules.rules.rule_test_example"].severity == Severity.CRITICAL


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


def test_rule_registry_rule_filters(valid_config_path, model1, model2):
    """Test config filters are loaded."""
    config = Config()
    config._load_toml_file(str(valid_config_path))
    r = RuleRegistry(config)
    r._load("tests.rules")
    r._load_filters_into_rules()

    assert not r.rules["tests.rules.rules.rule_test_example"].should_evaluate(model1)
    assert r.rules["tests.rules.rules.rule_test_example"].should_evaluate(model2)


def test_rule_registry_local_rules_from_project_dir(tmp_path, monkeypatch):
    """Ensure local rules are imported from the project directory, not the cwd."""
    project_dir = tmp_path / "my_project"
    package = project_dir / "project_dir_rules"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "rules.py").write_text(
        "from dbt_score import Model, RuleViolation, rule\n"
        "\n"
        "\n"
        "@rule\n"
        "def rule_from_project_dir(model: Model) -> RuleViolation | None:\n"
        '    """A local rule."""\n'
    )
    other_dir = tmp_path / "elsewhere"
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)
    monkeypatch.setattr("sys.path", list(__import__("sys").path))

    config = Config()
    config.rule_namespaces = ["project_dir_rules"]
    r = RuleRegistry(config)
    r.load_all(project_dir=project_dir)
    assert "project_dir_rules.rules.rule_from_project_dir" in r.rules
