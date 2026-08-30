"""Test models."""

from pathlib import Path
from unittest.mock import patch

from dbt_score.models import Exposure, ManifestLoader, Model, Snapshot


@patch("dbt_score.models.Path.read_text")
def test_manifest_load(mock_read_text, raw_manifest):
    """Test loading a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        loader = ManifestLoader(Path("some.json"))
        assert len(loader.models) == len(
            [
                node
                for node in raw_manifest["nodes"].values()
                if node["resource_type"] == "model"
                and node["package_name"] == raw_manifest["metadata"]["project_name"]
            ]
        )

        model1 = loader.models["model.package.model1"]
        assert model1.tests[0].name == "test2"
        assert model1.tests[1].name == "test4"

        column_a = model1.columns[0]
        assert column_a.name == "column_a"
        assert column_a.config.get("meta", {}).get("custom_property") == "custom_value"
        assert column_a.config.get("meta", {}).get("info") == "some info"
        assert column_a.tests[0].name == "test1"

        model2 = loader.models["model.package.model2"]
        column_a_model2 = model2.columns[0]
        assert column_a_model2.name == "column_a"
        assert column_a_model2.config == {}

        assert len(loader.sources) == len(
            [
                source
                for source in raw_manifest["sources"].values()
                if source["package_name"] == raw_manifest["metadata"]["project_name"]
            ]
        )
        assert (
            loader.sources["source.package.my_source.table1"].tests[0].name
            == "source_test1"
        )

        assert loader.snapshots["snapshot.package.snapshot1"].parents == [
            loader.models["model.package.model1"]
        ]
        assert loader.models["model.package.model1"].children == [
            loader.snapshots["snapshot.package.snapshot1"],
            loader.exposures["exposure.package.exposure1"],
        ]
        assert loader.models["model.package.model1"].parents == [
            loader.models["model.package.model2"],
            loader.sources["source.package.my_source.table1"],
            loader.snapshots["snapshot.package.snapshot2"],
        ]
        assert loader.models["model.package.model2"].children == [
            loader.models["model.package.model1"],
            loader.models["model.package.collision_test"],
            loader.exposures["exposure.package.exposure2"],
        ]
        assert loader.models["model.package.model2"].parents == [
            loader.seeds["seed.package.seed1"]
        ]
        assert loader.snapshots["snapshot.package.snapshot2"].parents == [
            loader.sources["source.package.my_source.table1"]
        ]
        assert loader.sources["source.package.my_source.table1"].children == [
            loader.models["model.package.model1"],
            loader.snapshots["snapshot.package.snapshot2"],
        ]
        assert loader.seeds["seed.package.seed1"].children == [
            loader.models["model.package.model2"]
        ]

        assert loader.models["model.package.collision_test"].parents == [
            loader.models["model.package.model2"]
        ]
        assert loader.models["model.package.collision_test"].children == [
            loader.exposures["exposure.package.exposure_collision"],
        ]
        assert loader.exposures["exposure.package.exposure1"].parents == [
            loader.models["model.package.model1"]
        ]
        assert loader.exposures["exposure.package.exposure_collision"].parents == [
            loader.models["model.package.collision_test"]
        ]

        assert len(loader.macros) == len(
            [
                macro
                for macro in raw_manifest["macros"].values()
                if macro["package_name"] == raw_manifest["metadata"]["project_name"]
            ]
        )
        macro1 = loader.macros["macro.package.macro1"]
        assert macro1.name == "macro1"
        assert macro1.description == "A helpful macro."
        assert macro1.tags == ["utility"]
        macro2 = loader.macros["macro.package.macro2"]
        assert macro2.name == "macro2"
        assert macro2.description == ""
        assert len(macro2.arguments) == 2


@patch("dbt_score.models.Path.read_text")
def test_manifest_select_models_simple(mock_read_text, raw_manifest):
    """Test a simple selection in a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["model1"])

    assert [x.name for x in manifest_loader.models.values()] == ["model1"]


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_models_dbt_ls(mock_dbt_ls, mock_read_text, raw_manifest):
    """Test a complex selection in a manifest, which uses dbt ls."""
    mock_dbt_ls.return_value = ["model1"]
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["+model1"])

    assert [x.name for x in manifest_loader.models.values()] == ["model1"]
    mock_dbt_ls.assert_called_once_with(["+model1"], None)


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_no_model(mock_dbt_ls, mock_read_text, raw_manifest, caplog):
    """Test the lack of model in a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["non_existing"])

    assert len(manifest_loader.models) == 0
    assert "Nothing to evaluate!" in caplog.text


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_exclude_simple(mock_dbt_ls, mock_read_text, chain_raw_manifest):
    """Exclude model1 — model1 is excluded, the rest are included."""
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(Path("some.json"), exclude=["model1"])

    assert sorted(m.name for m in loader.models.values()) == sorted(
        ["model0", "model2", "model3", "standalone"]
    )
    mock_dbt_ls.assert_not_called()


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_exclude_ancestors(mock_dbt_ls, mock_read_text, chain_raw_manifest):
    """Exclude +model1 — model0 and model1 are excluded, the rest are included."""
    mock_dbt_ls.return_value = ["model2", "model3", "standalone"]
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(Path("some.json"), exclude=["+model1"])

    assert sorted(m.name for m in loader.models.values()) == sorted(
        ["model2", "model3", "standalone"]
    )
    mock_dbt_ls.assert_called_once_with(None, ["+model1"])


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_exclude_descendants(mock_dbt_ls, mock_read_text, chain_raw_manifest):
    """Exclude model1+ — model0 and standalone are kept.

    model1, model2 and model3 are descendants of model1 (or model1 itself), so excluded.
    """
    mock_dbt_ls.return_value = ["model0", "standalone"]
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(Path("some.json"), exclude=["model1+"])

    assert sorted(m.name for m in loader.models.values()) == sorted(
        ["model0", "standalone"]
    )
    mock_dbt_ls.assert_called_once_with(None, ["model1+"])


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_exclude_non_existing(mock_dbt_ls, mock_read_text, chain_raw_manifest):
    """Exclude non_existing — all models are included since the model does not exist."""
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(Path("some.json"), exclude=["non_existing"])

    assert sorted(m.name for m in loader.models.values()) == sorted(
        ["model0", "model1", "model2", "model3", "standalone"]
    )
    mock_dbt_ls.assert_not_called()


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_and_exclude_simple(
    mock_dbt_ls, mock_read_text, chain_raw_manifest
):
    """Select model2 and exclude model1 — only model2 is included."""
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(
            Path("some.json"), select=["model2"], exclude=["model1"]
        )

    assert [m.name for m in loader.models.values()] == ["model2"]
    mock_dbt_ls.assert_not_called()


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_and_exclude_same_model(
    mock_dbt_ls, mock_read_text, chain_raw_manifest
):
    """Select model1 and exclude model1 — no models are included."""
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(
            Path("some.json"), select=["model1"], exclude=["model1"]
        )

    assert len(loader.models) == 0
    mock_dbt_ls.assert_not_called()


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_and_exclude_ancestors_complex(
    mock_dbt_ls, mock_read_text, chain_raw_manifest
):
    """Select +model1 and exclude +model1 — no models are included."""
    mock_dbt_ls.return_value = []
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(
            Path("some.json"), select=["+model1"], exclude=["+model1"]
        )

    assert len(loader.models) == 0
    mock_dbt_ls.assert_called_once()


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_simple_exclude_descendants(
    mock_dbt_ls, mock_read_text, chain_raw_manifest
):
    """Select model2 and exclude model1+ — no models included.

    model2 is a descendant of model1, so it is excluded.
    """
    mock_dbt_ls.return_value = []
    with patch("dbt_score.models.json.loads", return_value=chain_raw_manifest):
        loader = ManifestLoader(
            Path("some.json"), select=["model2"], exclude=["model1+"]
        )

    assert len(loader.models) == 0
    mock_dbt_ls.assert_called_once()


def create_dummy_model(unique_id: str, name: str = "dummy", children=None) -> Model:
    """Helper to create a minimal Model instance for testing."""
    return Model(
        unique_id=unique_id,
        name=name,
        relation_name="relation",
        description="desc",
        original_file_path="path.sql",
        config={},
        meta={},
        columns=[],
        package_name="pkg",
        database="db",
        schema="schema",
        raw_code="select 1",
        language="sql",
        access="public",
        group="group",
        parents=[],
        children=children or [],
    )


def create_dummy_snapshot(
    unique_id: str, name: str = "dummy", children=None
) -> Snapshot:
    """Helper to create a minimal Snapshot instance for testing."""
    return Snapshot(
        unique_id=unique_id,
        name=name,
        relation_name="relation",
        description="desc",
        original_file_path="path.sql",
        config={},
        meta={},
        columns=[],
        package_name="pkg",
        database="db",
        schema="schema",
        raw_code="select 1",
        language="sql",
        parents=[],
        children=children or [],
    )


def create_dummy_exposure(unique_id: str, name: str = "dummy") -> Exposure:
    """Helper to create a minimal Exposure instance for testing."""
    return Exposure(
        unique_id=unique_id,
        name=name,
        description="desc",
        label="label",
        url="http://url",
        maturity="high",
        original_file_path="path.yml",
        type="dashboard",
        owner={},
        config={},
        meta={},
        tags=[],
        parents=[],
    )


def test_downstream_count_isolated():
    """Verify that a standalone model with no children/dependents returns 0."""
    model = create_dummy_model("model.package.isolated", "isolated")
    assert model.downstream_count == 0


def test_downstream_count_single_child():
    """Verify that a model with exactly one child model returns 1."""
    child = create_dummy_model("model.package.child", "child")
    parent = create_dummy_model("model.package.parent", "parent", children=[child])
    assert parent.downstream_count == 1


def test_downstream_count_linear_chain():
    """Verify downstream_count calculation in a linear chain of dependencies."""
    grandchild = create_dummy_model("model.package.grandchild", "grandchild")
    child = create_dummy_model("model.package.child", "child", children=[grandchild])
    parent = create_dummy_model("model.package.parent", "parent", children=[child])
    assert parent.downstream_count == 2
    assert child.downstream_count == 1


def test_downstream_count_diamond_dag():
    """Verify downstream_count in a diamond dependency.

    Ensure the shared descendant is only counted once.
    """
    descendant = create_dummy_model("model.package.descendant", "descendant")
    child_b = create_dummy_model(
        "model.package.child_b", "child_b", children=[descendant]
    )
    child_c = create_dummy_model(
        "model.package.child_c", "child_c", children=[descendant]
    )
    parent = create_dummy_model(
        "model.package.parent", "parent", children=[child_b, child_c]
    )
    assert parent.downstream_count == 3


def test_downstream_count_with_non_model_descendants():
    """Verify only Model instances are counted.

    Ensure non-model nodes are traversed correctly.
    """
    exposure = create_dummy_exposure("exposure.package.exp")
    snapshot = create_dummy_snapshot(
        "snapshot.package.snap", "snap", children=[exposure]
    )
    model = create_dummy_model("model.package.m", "m")

    # Snapshot (not Model) has exposure (not Model) and model (Model)
    snapshot.children.append(model)

    # Root model has snapshot
    parent = create_dummy_model("model.package.parent", "parent", children=[snapshot])

    # Only model should be counted (1), snapshot and exposure are not Model type
    assert parent.downstream_count == 1


def test_group_owner_loaded(raw_manifest):
    """Test that group owner is correctly loaded for models."""
    with patch("dbt_score.models.Path.read_text"):
        with patch("dbt_score.models.json.loads", return_value=raw_manifest):
            loader = ManifestLoader(Path("some.json"))
            assert len(loader.groups) == 2
            assert "group.package.them_over_there" in loader.groups
            group = loader.groups["group.package.them_over_there"]
            assert group.name == "them_over_there"
            assert group.owner is not None
            assert group.owner.name == "Alice"
            assert group.owner.email == "alice@example.com"

            model_with_owner = loader.models["model.package.model2"]
            assert model_with_owner.group == "them_over_there"
            assert model_with_owner.group_owner is not None
            assert model_with_owner.group_owner.name == "Alice"
            assert model_with_owner.group_owner.email == "alice@example.com"

            model_without_owner = loader.models["model.package.collision_test"]
            assert model_without_owner.group == "default"
            assert model_without_owner.group_owner is not None
            assert model_without_owner.group_owner.name is None
            assert model_without_owner.group_owner.email is None

            model_no_group = loader.models["model.package.model1"]
            assert model_no_group.group is None
            assert model_no_group.group_owner is None


def test_group_owner_with_list_email():
    """Test group owner with email as list."""
    raw_manifest = {
        "metadata": {"project_name": "package"},
        "nodes": {
            "model.package.m1": {
                "resource_type": "model",
                "package_name": "package",
                "unique_id": "model.package.m1",
                "name": "m1",
                "relation_name": "db.schema.m1",
                "description": "",
                "original_file_path": "/path/m1.sql",
                "config": {},
                "meta": {},
                "columns": {},
                "constraints": [],
                "database": "db",
                "schema": "schema",
                "raw_code": "select 1",
                "alias": "m1",
                "patch_path": None,
                "tags": [],
                "depends_on": {"nodes": []},
                "language": "sql",
                "access": "public",
                "group": "my_group",
            }
        },
        "sources": {},
        "exposures": {},
        "macros": {},
        "groups": {
            "group.package.my_group": {
                "name": "my_group",
                "resource_type": "group",
                "package_name": "package",
                "path": "models/_groups.yml",
                "original_file_path": "models/_groups.yml",
                "unique_id": "group.package.my_group",
                "owner": {
                    "name": "Bob",
                    "email": ["bob@example.com", "bob2@example.com"],
                },
                "description": None,
                "config": {},
            }
        },
    }
    with patch("dbt_score.models.Path.read_text"):
        with patch("dbt_score.models.json.loads", return_value=raw_manifest):
            loader = ManifestLoader(Path("some.json"))
            model = loader.models["model.package.m1"]
            assert model.group_owner is not None
            assert model.group_owner.name == "Bob"
            assert model.group_owner.email == ["bob@example.com", "bob2@example.com"]


def test_model_without_group_key():
    """Test that model without group key is handled."""
    raw_manifest = {
        "metadata": {"project_name": "package"},
        "nodes": {
            "model.package.m1": {
                "resource_type": "model",
                "package_name": "package",
                "unique_id": "model.package.m1",
                "name": "m1",
                "relation_name": "db.schema.m1",
                "description": "",
                "original_file_path": "/path/m1.sql",
                "config": {},
                "meta": {},
                "columns": {},
                "constraints": [],
                "database": "db",
                "schema": "schema",
                "raw_code": "select 1",
                "alias": "m1",
                "patch_path": None,
                "tags": [],
                "depends_on": {"nodes": []},
                "language": "sql",
                "access": "public",
            }
        },
        "sources": {},
        "exposures": {},
        "macros": {},
        "groups": {},
    }
    with patch("dbt_score.models.Path.read_text"):
        with patch("dbt_score.models.json.loads", return_value=raw_manifest):
            loader = ManifestLoader(Path("some.json"))
            model = loader.models["model.package.m1"]
            assert model.group is None
            assert model.group_owner is None


def test_manifest_without_groups(raw_manifest):
    """Test that manifest without groups still loads."""
    raw_manifest_no_groups = {k: v for k, v in raw_manifest.items() if k != "groups"}
    raw_manifest_no_groups.pop("group_map", None)
    with patch("dbt_score.models.Path.read_text"):
        with patch("dbt_score.models.json.loads", return_value=raw_manifest_no_groups):
            loader = ManifestLoader(Path("some.json"))
            assert len(loader.groups) == 0
            assert loader.models["model.package.model2"].group == "them_over_there"
            assert loader.models["model.package.model2"].group_owner is None
