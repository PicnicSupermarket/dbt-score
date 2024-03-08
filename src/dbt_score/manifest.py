from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Constraint:
    """Constraint for a column in a model."""

    type: str
    expression: str
    name: str


@dataclass
class Test:
    """Test for a column or model."""

    name: str
    type: str
    tags: list[str] = field(default_factory=list)


@dataclass
class Column:
    """Represents a column in a model."""

    name: str
    description: str
    constraints: List[Constraint]
    tests: List[Test] = field(default_factory=list)


@dataclass
class Model:
    """Represents a dbt model."""

    id: str
    name: str
    description: str
    file_path: str
    config: dict[str, Any]
    meta: dict[str, Any]
    columns: dict[str, Column]
    tests: list[Test] = field(default_factory=list)

    @classmethod
    def from_node(cls, node_values: dict[str, Any]) -> "Model":
        """Create a model object from a node in the manifest."""
        columns = {
            name: Column(
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
            )
            for name, values in node_values.get("columns", {}).items()
        }

        model = cls(
            id=node_values["unique_id"],
            file_path=node_values["patch_path"],
            config=node_values.get("config", {}),
            name=node_values["name"],
            description=node_values.get("description", ""),
            meta=node_values.get("meta", {}),
            columns=columns,
        )

        return model


class ManifestLoader:
    """Load the models and tests from the manifest."""

    def __init__(self, raw_manifest: dict[str, Any]):
        self.raw_manifest = raw_manifest
        self.raw_nodes = raw_manifest.get("nodes", {})
        self.models: dict[str, Model] = {}
        self.tests: dict[str, Test] = {}

        # Load models first so the tests can be attached to them later.
        self.load_models()
        self.load_tests()

    def load_models(self) -> None:
        """Load the models from the manifest."""
        for node_values in self.raw_nodes.values():
            if node_values.get("resource_type") == "model":
                model = Model.from_node(node_values)
                self.models[model.id] = model

    def load_tests(self) -> None:
        """Load the tests from the manifest and attach them to the right object."""
        for node_values in self.raw_nodes.values():
            # Only include tests that are attached to a model.
            if node_values.get("resource_type") == "test" and node_values.get(
                "attached_node"
            ):
                model = self.models.get(node_values.get("attached_node"))

                if not model:
                    raise ValueError(
                        f"Model {node_values.get('attached_node')}"
                        f"not found, while tests are attached to it."
                    )

                test = Test(
                    name=node_values.get("name"),
                    type=node_values.get("test_metadata").get("name"),
                    tags=node_values.get("tags"),
                )
                column_name = (
                    node_values.get("test_metadata").get("kwargs").get("column_name")
                )

                if column_name:  # Test is a column-level test.
                    model.columns[column_name].tests.append(test)
                else:
                    model.tests.append(test)
