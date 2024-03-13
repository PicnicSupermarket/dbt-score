"""Objects related to loading the dbt manifest."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Constraint:
    """Constraint for a column.

    Args:
        name: The name of the constraint.
        type: The type of the constraint, e.g. `foreign_key`.
        expression: The expression of the constraint, e.g. `schema.other_table`.
    """

    name: str
    type: str
    expression: str


@dataclass
class Test:
    """Test for a column or model.

    Args:
        name: The name of the test.
        type: The type of the test, e.g. `unique`.
        tags: The list of tags attached to the test.
    """

    name: str
    type: str
    tags: list[str] = field(default_factory=list)


@dataclass
class Column:
    """Represents a column in a model.

    Args:
        name: The name of the column.
        description: The description of the column.
        constraints: The list of constraints attached to the column.
        tests: The list of tests attached to the column.
    """

    name: str
    description: str
    constraints: list[Constraint] = field(default_factory=list)
    tests: list[Test] = field(default_factory=list)


@dataclass
class Model:
    """Represents a dbt model.

    Args:
        id: The id of the model, e.g. `model.package.model_name`.
        name: The name of the model.
        description: The full description of the model.
        file_path: The `.yml` file path of the model.
        config: The config of the model.
        meta: The meta of the model.
        columns: The list of columns of the model.
        tests: The list of tests attached to the model.
    """

    id: str
    name: str
    description: str
    file_path: str
    config: dict[str, Any]
    meta: dict[str, Any]
    columns: list[Column]
    tests: list[Test] = field(default_factory=list)

    def get_column(self, column_name: str) -> Column | None:
        """Get a column by name."""
        for column in self.columns:
            if column.name == column_name:
                return column

        return None

    @staticmethod
    def _get_columns(
        node_values: dict[str, Any], tests_values: list[dict[str, Any]]
    ) -> list[Column]:
        """Get columns from a node and it's tests in the manifest."""
        columns = [
            Column(
                name=values.get("name"),
                description=values.get("description"),
                constraints=[
                    Constraint(
                        name=constraint.get("name"),
                        type=constraint.get("type"),
                        expression=constraint.get("expression"),
                    )
                    for constraint in values.get("constraints", [])
                ],
                tests=[
                    Test(
                        name=test["name"],
                        type=test["test_metadata"]["name"],
                        tags=test.get("tags", []),
                    )
                    for test in tests_values
                    if test["test_metadata"].get("kwargs", {}).get("column_name")
                    == values.get("name")
                ],
            )
            for name, values in node_values.get("columns", {}).items()
        ]
        return columns

    @classmethod
    def from_node(
        cls, node_values: dict[str, Any], tests_values: list[dict[str, Any]]
    ) -> "Model":
        """Create a model object from a node and it's tests in the manifest."""
        model = cls(
            id=node_values["unique_id"],
            file_path=node_values["patch_path"],
            config=node_values.get("config", {}),
            name=node_values["name"],
            description=node_values.get("description", ""),
            meta=node_values.get("meta", {}),
            columns=cls._get_columns(node_values, tests_values),
            tests=[
                Test(
                    name=test["name"],
                    type=test["test_metadata"]["name"],
                    tags=test.get("tags", []),
                )
                for test in tests_values
                if not test["test_metadata"].get("kwargs", {}).get("column_name")
            ],
        )

        return model


class ManifestLoader:
    """Load the models and tests from the manifest."""

    def __init__(self, raw_manifest: dict[str, Any]):
        """Initialize the ManifestLoader.

        Args:
            raw_manifest: The dictionary representation of the JSON manifest.
        """
        self.raw_manifest = raw_manifest
        self.raw_nodes = raw_manifest.get("nodes", {})
        self.models: list[Model] = []
        self.tests: dict[str, list[dict[str, Any]]] = defaultdict(list)

        self._reindex_tests()
        self._load_models()

    def _load_models(self) -> None:
        """Load the models from the manifest."""
        for node_id, node_values in self.raw_nodes.items():
            if node_values.get("resource_type") == "model":
                model = Model.from_node(node_values, self.tests.get(node_id, []))
                self.models.append(model)

    def _reindex_tests(self) -> None:
        """Index tests based on their model id."""
        for node_values in self.raw_nodes.values():
            # Only include tests that are attached to a model.
            if node_values.get("resource_type") == "test" and node_values.get(
                "attached_node"
            ):
                self.tests[node_values["attached_node"]].append(node_values)
