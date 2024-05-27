"""Test configuration."""

import json
from pathlib import Path
from typing import Any, Type

from dbt_score import Model, Rule, RuleViolation, Severity, rule
from dbt_score.config import Config
from dbt_score.models import ManifestLoader
from pytest import fixture

# Configuration


@fixture()
def default_config() -> Config:
    """Return a default Config object."""
    return Config()


@fixture
def valid_config_path() -> Path:
    """Return the path of the configuration."""
    return Path(__file__).parent / "resources" / "pyproject.toml"


@fixture
def invalid_config_path() -> Path:
    """Return the path of the configuration."""
    return Path(__file__).parent / "resources" / "invalid_pyproject.toml"


# Manifest


@fixture
def manifest_empty_path() -> Path:
    """Return the path of an empty manifest."""
    return Path(__file__).parent / "resources" / "manifest_empty.json"


@fixture
def manifest_path() -> Path:
    """Return the path of a manifest."""
    return Path(__file__).parent / "resources" / "manifest.json"


@fixture
def raw_manifest(manifest_path) -> Any:
    """Return a raw manifest."""
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@fixture
def manifest_loader(manifest_path) -> ManifestLoader:
    """Return an instantiated and loaded manifest loader."""
    return ManifestLoader(file_path=manifest_path)


# Models


@fixture
def model1(raw_manifest) -> Model:
    """Model 1."""
    return Model.from_node(raw_manifest["nodes"]["model.package.model1"], [])


@fixture
def model2(raw_manifest) -> Model:
    """Model 2."""
    return Model.from_node(raw_manifest["nodes"]["model.package.model2"], [])


# Multiple ways to create rules


@fixture
def decorator_rule() -> Type[Rule]:
    """An example rule created with the rule decorator."""

    @rule()
    def example_rule(model: Model) -> RuleViolation | None:
        """Description of the rule."""
        if model.name == "model1":
            return RuleViolation(message="Model1 is a violation.")

    return example_rule


@fixture
def decorator_rule_no_parens() -> Type[Rule]:
    """An example rule created with the rule decorator without parentheses."""

    @rule
    def example_rule(model: Model) -> RuleViolation | None:
        """Description of the rule."""
        if model.name == "model1":
            return RuleViolation(message="Model1 is a violation.")

    return example_rule


@fixture
def decorator_rule_args() -> Type[Rule]:
    """An example rule created with the rule decorator with arguments."""

    @rule(description="Description of the rule.")
    def example_rule(model: Model) -> RuleViolation | None:
        if model.name == "model1":
            return RuleViolation(message="Model1 is a violation.")

    return example_rule


@fixture
def class_rule() -> Type[Rule]:
    """An example rule created with a class."""

    class ExampleRule(Rule):
        """Example rule."""

        description = "Description of the rule."

        def evaluate(self, model: Model) -> RuleViolation | None:
            """Evaluate model."""
            if model.name == "model1":
                return RuleViolation(message="Model1 is a violation.")

    return ExampleRule


# Rules


@fixture
def rule_severity_low() -> Type[Rule]:
    """An example rule with LOW severity."""

    @rule(severity=Severity.LOW)
    def rule_severity_low(model: Model) -> RuleViolation | None:
        """Rule with LOW severity."""
        if model.name != "model1":
            return RuleViolation(message="Linting error")

    return rule_severity_low


@fixture
def rule_severity_medium() -> Type[Rule]:
    """An example rule with MEDIUM severity."""

    @rule(severity=Severity.MEDIUM)
    def rule_severity_medium(model: Model) -> RuleViolation | None:
        """Rule with MEDIUM severity."""
        if model.name != "model1":
            return RuleViolation(message="Linting error")

    return rule_severity_medium


@fixture
def rule_severity_high() -> Type[Rule]:
    """An example rule with HIGH severity."""

    @rule(severity=Severity.HIGH)
    def rule_severity_high(model: Model) -> RuleViolation | None:
        """Rule with HIGH severity."""
        if model.name != "model1":
            return RuleViolation(message="Linting error")

    return rule_severity_high


@fixture
def rule_severity_critical() -> Type[Rule]:
    """An example rule with CRITICAL severity."""

    @rule(severity=Severity.CRITICAL)
    def rule_severity_critical(model: Model) -> RuleViolation | None:
        """Rule with CRITICAL severity."""
        if model.name != "model1":
            return RuleViolation(message="Linting error")

    return rule_severity_critical


@fixture
def rule_with_config() -> Type[Rule]:
    """An example rule with additional configuration."""

    @rule
    def rule_with_config(
        model: Model, model_name: str = "model1"
    ) -> RuleViolation | None:
        """Rule with additional configuration."""
        if model.name != model_name:
            return RuleViolation(message=model_name)

    return rule_with_config


@fixture
def rule_error() -> Type[Rule]:
    """An example rule which fails to run."""

    @rule
    def rule_error(model: Model) -> RuleViolation | None:
        """Always failing rule."""
        raise Exception("Oh noes, something went wrong")

    return rule_error
