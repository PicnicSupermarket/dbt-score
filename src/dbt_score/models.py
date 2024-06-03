"""Objects related to loading the dbt manifest."""

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from dbt_score.dbt_utils import dbt_ls

logger = logging.getLogger(__name__)


@dataclass
class Constraint:
    """Constraint for a column.

    Attributes:
        type: The type of the constraint, e.g. `foreign_key`.
        name: The name of the constraint.
        expression: The expression of the constraint, e.g. `schema.other_table`.
        _raw_values: The raw values of the constraint in the manifest.
    """

    type: str
    name: str | None = None
    expression: str | None = None
    _raw_values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_raw_values(cls, raw_values: dict[str, Any]) -> "Constraint":
        """Create a constraint object from a constraint node in the manifest."""
        return cls(
            type=raw_values["type"],
            name=raw_values["name"],
            expression=raw_values["expression"],
            _raw_values=raw_values,
        )


@dataclass
class Test:
    """Test for a column or model.

    Attributes:
        name: The name of the test.
        type: The type of the test, e.g. `unique`.
        kwargs: The kwargs of the test.
        tags: The list of tags attached to the test.
        _raw_values: The raw values of the test in the manifest.
    """

    name: str
    type: str
    kwargs: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    _raw_values: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_node(cls, test_node: dict[str, Any]) -> "Test":
        """Create a test object from a test node in the manifest."""
        return cls(
            name=test_node["name"],
            type=test_node["test_metadata"]["name"],
            kwargs=test_node["test_metadata"].get("kwargs", {}),
            tags=test_node.get("tags", []),
            _raw_values=test_node,
        )


@dataclass
class Column:
    """Represents a column in a model.

    Attributes:
        name: The name of the column.
        description: The description of the column.
        data_type: The data type of the column.
        meta: The metadata attached to the column.
        constraints: The list of constraints attached to the column.
        tags: The list of tags attached to the column.
        tests: The list of tests attached to the column.
        _raw_values: The raw values of the column as defined in the node.
        _raw_test_values: The raw test values of the column as defined in the node.
    """

    name: str
    description: str
    data_type: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    constraints: list[Constraint] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    tests: list[Test] = field(default_factory=list)
    _raw_values: dict[str, Any] = field(default_factory=dict)
    _raw_test_values: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_node_values(
        cls, values: dict[str, Any], test_values: list[dict[str, Any]]
    ) -> "Column":
        """Create a column object from raw values."""
        return cls(
            name=values["name"],
            description=values["description"],
            data_type=values["data_type"],
            meta=values["meta"],
            constraints=[
                Constraint.from_raw_values(constraint)
                for constraint in values["constraints"]
            ],
            tags=values["tags"],
            tests=[Test.from_node(test) for test in test_values],
            _raw_values=values,
            _raw_test_values=test_values,
        )


@dataclass
class Model:
    """Represents a dbt model.

    Attributes:
        unique_id: The id of the model, e.g. `model.package.model_name`.
        name: The name of the model.
        relation_name: The relation name of the model, e.g. `db.schema.model_name`.
        description: The full description of the model.
        original_file_path: The sql path of the model, `e.g. model_dir/dir/file.sql`.
        config: The config of the model.
        meta: The meta of the model.
        columns: The list of columns of the model.
        package_name: The package name of the model.
        database: The database name of the model.
        schema: The schema name of the model.
        raw_code: The raw code of the model.
        language: The language of the model, e.g. sql.
        access: The access level of the model, e.g. public.
        alias: The alias of the model.
        patch_path: The yml path of the model, e.g. `package://model_dir/dir/file.yml`.
        tags: The list of tags attached to the model.
        tests: The list of tests attached to the model.
        depends_on: Dictionary of models/sources/macros that the model depends on.
        _raw_values: The raw values of the model (node) in the manifest.
        _raw_test_values: The raw test values of the model (node) in the manifest.
    """

    unique_id: str
    name: str
    relation_name: str
    description: str
    original_file_path: str
    config: dict[str, Any]
    meta: dict[str, Any]
    columns: list[Column]
    package_name: str
    database: str
    schema: str
    raw_code: str
    language: str
    access: str
    alias: str | None = None
    patch_path: str | None = None
    tags: list[str] = field(default_factory=list)
    tests: list[Test] = field(default_factory=list)
    depends_on: dict[str, list[str]] = field(default_factory=dict)
    _raw_values: dict[str, Any] = field(default_factory=dict)
    _raw_test_values: list[dict[str, Any]] = field(default_factory=list)

    def get_column(self, column_name: str) -> Column | None:
        """Get a column by name."""
        for column in self.columns:
            if column.name == column_name:
                return column

        return None

    @staticmethod
    def _get_columns(
        node_values: dict[str, Any], test_values: list[dict[str, Any]]
    ) -> list[Column]:
        """Get columns from a node and its tests in the manifest."""
        return [
            Column.from_node_values(
                values,
                [
                    test
                    for test in test_values
                    if test["test_metadata"]["kwargs"].get("column_name") == name
                ],
            )
            for name, values in node_values.get("columns", {}).items()
        ]

    @classmethod
    def from_node(
        cls, node_values: dict[str, Any], test_values: list[dict[str, Any]]
    ) -> "Model":
        """Create a model object from a node and it's tests in the manifest."""
        return cls(
            unique_id=node_values["unique_id"],
            name=node_values["name"],
            relation_name=node_values["relation_name"],
            description=node_values["description"],
            original_file_path=node_values["original_file_path"],
            config=node_values["config"],
            meta=node_values["meta"],
            columns=cls._get_columns(node_values, test_values),
            package_name=node_values["package_name"],
            database=node_values["database"],
            schema=node_values["schema"],
            raw_code=node_values["raw_code"],
            language=node_values["language"],
            access=node_values["access"],
            alias=node_values["alias"],
            patch_path=node_values["patch_path"],
            tags=node_values["tags"],
            tests=[
                Test.from_node(test)
                for test in test_values
                if not test["test_metadata"]["kwargs"].get("column_name")
            ],
            depends_on=node_values["depends_on"],
            _raw_values=node_values,
            _raw_test_values=test_values,
        )

    def __hash__(self) -> int:
        """Compute a unique hash for a model."""
        return hash(self.unique_id)


class ManifestLoader:
    """Load the models and tests from the manifest."""

    def __init__(self, file_path: Path, select: Iterable[str] | None = None):
        """Initialize the ManifestLoader.

        Args:
            file_path: The file path of the JSON manifest.
            select: An optional dbt selection.
        """
        self.raw_manifest = json.loads(file_path.read_text(encoding="utf-8"))
        self.raw_nodes = self.raw_manifest.get("nodes", {})
        self.models: list[Model] = []
        self.tests: dict[str, list[dict[str, Any]]] = defaultdict(list)

        self._reindex_tests()
        self._load_models()

        if select:
            self._select_models(select)

        if len(self.models) == 0:
            logger.warning("No model found.")

    def _load_models(self) -> None:
        """Load the models from the manifest."""
        for node_id, node_values in self.raw_nodes.items():
            if node_values.get("resource_type") == "model":
                model = Model.from_node(node_values, self.tests.get(node_id, []))
                self.models.append(model)

    def _reindex_tests(self) -> None:
        """Index tests based on their model id."""
        for node_values in self.raw_nodes.values():
            # Only include tests that are attached to a model
            if node_values.get("resource_type") == "test" and (
                attached_node := node_values.get("attached_node")
            ):
                self.tests[attached_node].append(node_values)

    def _select_models(self, select: Iterable[str]) -> None:
        """Filter models like dbt's --select."""
        single_model_select = re.compile(r"[a-zA-Z0-9_]+")

        if all(single_model_select.fullmatch(x) for x in select):
            # Using '--select my_model' is a common case, which can easily be sped up by
            # not invoking dbt
            selected = select
        else:
            # Use dbt's implementation of --select
            selected = dbt_ls(select)

        self.models = [x for x in self.models if x.name in selected]
