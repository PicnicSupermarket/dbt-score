"""Objects related to loading the dbt manifest."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Constraint:
    """Constraint for a column.

    Attributes:
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

    Attributes:
        name: The name of the test.
        type: The type of the test, e.g. `unique`.
        kwargs: The kwargs of the test.
        tags: The list of tags attached to the test.
    """

    name: str
    type: str
    kwargs: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_node(cls, test_node: dict[str, Any]) -> "Test":
        """Create a test object from a test node in the manifest."""
        test = cls(
            name=test_node["name"],
            type=test_node["test_metadata"]["name"],
            kwargs=test_node["test_metadata"].get("kwargs", {}),
            tags=test_node.get("tags", []),
        )
        return test


@dataclass
class Column:
    """Represents a column in a model.

    Attributes:
        name: The name of the column.
        description: The description of the column.
        constraints: The list of constraints attached to the column.
        tags: The list of tags attached to the column.
        tests: The list of tests attached to the column.
    """

    name: str
    description: str
    constraints: list[Constraint] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    tests: list[Test] = field(default_factory=list)


@dataclass
class Model:
    """Represents a dbt model.

    Attributes:
        unique_id: The id of the model, e.g. `model.package.model_name`.
        name: The name of the model.
        description: The full description of the model.
        patch_path: The yml path of the model, e.g. `package://model_dir/dir/file.yml`.
        original_file_path: The sql path of the model, `e.g. model_dir/dir/file.sql`.
        config: The config of the model.
        meta: The meta of the model.
        columns: The list of columns of the model.
        package_name: The package name of the model.
        database: The database name of the model.
        schema: The schema name of the model.
        tags: The list of tags attached to the model.
        tests: The list of tests attached to the model.
        depends_on: Dictionary of models/sources/macros that the model depends on.
    """

    unique_id: str
    name: str
    description: str
    patch_path: str
    original_file_path: str
    config: dict[str, Any]
    meta: dict[str, Any]
    columns: list[Column]
    package_name: str
    database: str
    schema: str
    tags: list[str] = field(default_factory=list)
    tests: list[Test] = field(default_factory=list)
    depends_on: dict[str, list[str]] = field(default_factory=dict)

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
                tags=values.get("tags", []),
                tests=[
                    Test.from_node(test)
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
            unique_id=node_values["unique_id"],
            name=node_values["name"],
            description=node_values.get("description", ""),
            patch_path=node_values["patch_path"],
            original_file_path=node_values["original_file_path"],
            config=node_values.get("config", {}),
            meta=node_values.get("meta", {}),
            columns=cls._get_columns(node_values, tests_values),
            package_name=node_values["package_name"],
            database=node_values["database"],
            schema=node_values["schema"],
            tags=node_values.get("tags", []),
            tests=[
                Test.from_node(test)
                for test in tests_values
                if not test["test_metadata"].get("kwargs", {}).get("column_name")
            ],
            depends_on=node_values.get("depends_on", {}),
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
            if node_values.get("resource_type") == "test" and (
                attached_node := node_values.get("attached_node")
            ):
                self.tests[attached_node].append(node_values)
