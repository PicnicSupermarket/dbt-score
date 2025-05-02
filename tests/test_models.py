"""Test models."""

from pathlib import Path
from unittest.mock import patch

from dbt_score.models import ManifestLoader


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

        model1 = next(iter(loader.models.values())) if loader.models else None
        assert model1 is not None
        assert model1.tests[0].name == "test2"
        assert model1.tests[1].name == "test4"
        assert model1.columns[0].tests[0].name == "test1"

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
        assert loader.models["model.package.model1"].parents == [
            loader.models["model.package.model2"],
            loader.sources["source.package.my_source.table1"],
            loader.snapshots["snapshot.package.snapshot2"],
        ]
        assert loader.models["model.package.model2"].parents == []
        assert loader.snapshots["snapshot.package.snapshot2"].parents == [
            loader.sources["source.package.my_source.table1"]
        ]


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
    mock_dbt_ls.assert_called_once_with(["+model1"])


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_no_model(mock_dbt_ls, mock_read_text, raw_manifest, caplog):
    """Test the lack of model in a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["non_existing"])

    assert len(manifest_loader.models) == 0
    assert "Nothing to evaluate!" in caplog.text


@patch("dbt_score.models.Path.read_text")
def test_parent_references(mock_read_text, raw_manifest):
    """Test that parent references are correctly populated."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        loader = ManifestLoader(Path("some.json"))

        # Find models by direct lookup or by iterating and matching
        model1 = next((m for m in loader.models.values() if m.name == "model1"), None)
        model2 = next((m for m in loader.models.values() if m.name == "model2"), None)
        snapshot1 = next(
            (s for s in loader.snapshots.values() if s.name == "snapshot1"), None
        )
        snapshot2 = next(
            (s for s in loader.snapshots.values() if s.name == "snapshot2"), None
        )
        source1 = next((s for s in loader.sources.values() if s.name == "table1"), None)

        assert model1 is not None
        assert model2 is not None
        assert snapshot1 is not None
        assert snapshot2 is not None
        assert source1 is not None

        # Check parent relationships
        assert model1 in snapshot1.parents
        assert source1 in snapshot2.parents

        # Verify that model1 has the correct parents according to test data
        assert model2 in model1.parents
        assert source1 in model1.parents
        assert snapshot2 in model1.parents

        # Test a model with multiple parents
        # Find models with multiple dependencies in depends_on.nodes
        for node_id, node_values in raw_manifest["nodes"].items():
            if (
                node_id.startswith("model.")
                and len(node_values.get("depends_on", {}).get("nodes", [])) > 1
            ):
                model_with_deps = loader.models.get(node_id)
                if model_with_deps is not None:
                    # Verify all dependencies are in the parents list
                    for dep_id in node_values["depends_on"].get("nodes", []):
                        # Check each type of parent separately
                        parent_found = False

                        if dep_id in loader.models:
                            parent_model = loader.models[dep_id]
                            assert parent_model in model_with_deps.parents
                            parent_found = True
                        elif dep_id in loader.sources:
                            parent_source = loader.sources[dep_id]
                            assert parent_source in model_with_deps.parents
                            parent_found = True
                        elif dep_id in loader.snapshots:
                            parent_snapshot = loader.snapshots[dep_id]
                            assert parent_snapshot in model_with_deps.parents
                            parent_found = True
                        elif dep_id in loader.seeds:
                            parent_seed = loader.seeds[dep_id]
                            assert parent_seed in model_with_deps.parents
                            parent_found = True

                        if dep_id.startswith(
                            ("model.", "source.", "snapshot.", "seed.")
                        ):
                            assert (
                                parent_found
                            ), f"Dependency {dep_id} should be in parents"
