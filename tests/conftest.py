"""Test configuration."""
from typing import Any, Type

from dbt_score.models import Model
from dbt_score.rule import Rule, RuleViolation, rule
from pytest import ExitCode, Session, fixture


def pytest_sessionfinish(session: Session, exitstatus: int):
    """Avoid ci failure if no tests are found."""
    if exitstatus == ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = ExitCode.OK


@fixture
def raw_manifest() -> dict[str, Any]:
    """Mock the raw manifest."""
    return {
        "nodes": {
            "analysis.package.analysis1": {"resource_type": "analysis"},
            "model.package.model1": {
                "resource_type": "model",
                "unique_id": "model.package.model1",
                "name": "model1",
                "relation_name": "database.schema.model1",
                "description": "Description1.",
                "original_file_path": "/path/to/model1.sql",
                "config": {},
                "meta": {},
                "columns": {
                    "a": {
                        "name": "column_a",
                        "description": "Column A.",
                        "data_type": "string",
                        "meta": {},
                        "constraints": [],
                        "tags": [],
                    }
                },
                "package_name": "package",
                "database": "db",
                "schema": "schema",
                "raw_code": "SELECT x FROM y",
                "alias": "model1_alias",
                "patch_path": "/path/to/model1.yml",
                "tags": [],
                "depends_on": {},
            },
            "model.package.model2": {
                "resource_type": "model",
                "unique_id": "model.package.model2",
                "name": "model2",
                "relation_name": "database.schema.model2",
                "description": "Description2.",
                "original_file_path": "/path/to/model2.sql",
                "config": {},
                "meta": {},
                "columns": {
                    "a": {
                        "name": "column_a",
                        "description": "Column A.",
                        "data_type": "string",
                        "meta": {},
                        "constraints": [],
                        "tags": [],
                    }
                },
                "package_name": "package",
                "database": "db",
                "schema": "schema",
                "raw_code": "SELECT x FROM y",
                "alias": "model2_alias",
                "patch_path": "/path/to/model2.yml",
                "tags": [],
                "depends_on": {},
            },
            "test.package.test1": {
                "resource_type": "test",
                "attached_node": "model.package.model1",
                "name": "test1",
                "test_metadata": {"name": "type", "kwargs": {"column_name": "a"}},
                "tags": [],
            },
            "test.package.test2": {
                "resource_type": "test",
                "attached_node": "model.package.model1",
                "name": "test2",
                "test_metadata": {"name": "type", "kwargs": {}},
                "tags": [],
            },
            "test.package.test3": {"resource_type": "test"},
        }
    }


@fixture
def model1(raw_manifest) -> Model:
    """Model 1."""
    return Model.from_node(raw_manifest["nodes"]["model.package.model1"], [])


@fixture
def model2(raw_manifest) -> Model:
    """Model 2."""
    return Model.from_node(raw_manifest["nodes"]["model.package.model2"], [])


@fixture
def decorator_rule() -> Type[Rule]:
    """An example rule created with the rule decorator."""

    @rule()
    def example_rule(model: Model) -> RuleViolation | None:
        """Description of the rule."""
        if model.name == "model1":
            return RuleViolation(message="Model1 is a violation.")
        return None

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
            return None

    return ExampleRule


@fixture
def invalid_class_rule() -> Type[Rule]:
    """An example rule created with a class."""

    class ExampleRule(Rule):
        """Example rule."""

        description = "Description of the rule."

        def evaluate(self, model: Model) -> RuleViolation | None:
            """Evaluate model."""
            if model.name == "model1":
                return RuleViolation(message="Model1 is a violation.")
            return None

    return ExampleRule
