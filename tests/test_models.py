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

        model1 = loader.get_first_model()
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

        source1 = loader.get_first_source()
        assert source1 is not None
        assert source1.tests[0].name == "source_test1"


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
def test_helper_methods(mock_read_text, raw_manifest):
    """Test the helper methods to find models by name."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        loader = ManifestLoader(Path("some.json"))

        # Test get_model_by_name
        model1 = loader.get_model_by_name("model1")
        model2 = loader.get_model_by_name("model2")
        assert model1 is not None
        assert model2 is not None
        assert model1.name == "model1"
        assert model2.name == "model2"

        # Test get_first_model
        first_model = loader.get_first_model()
        assert first_model is not None
        assert first_model.name in ["model1", "model2"]

        # Test get_source_by_name
        source1 = loader.get_source_by_name("table1")
        source2 = loader.get_source_by_name("table2")
        assert source1 is not None
        assert source2 is not None
        assert source1.name == "table1"
        assert source2.name == "table2"

        # Test get_source_by_selector_name
        source1_sel = loader.get_source_by_selector_name("my_source.table1")
        assert source1_sel is not None
        assert source1_sel.name == "table1"
        assert source1_sel.source_name == "my_source"

        # Test get_snapshot_by_name
        snapshot1 = loader.get_snapshot_by_name("snapshot1")
        assert snapshot1 is not None
        assert snapshot1.name == "snapshot1"

        # Test with non-existent names
        assert loader.get_model_by_name("non_existent") is None
        assert loader.get_source_by_name("non_existent") is None
        assert loader.get_snapshot_by_name("non_existent") is None


@patch("dbt_score.models.Path.read_text")
def test_parent_references(mock_read_text, raw_manifest):
    """Test that parent references are correctly populated."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        loader = ManifestLoader(Path("some.json"))

        # Get models to check parent relationships
        model2 = loader.get_model_by_name("model2")
        snapshot1 = loader.get_snapshot_by_name("snapshot1")

        assert model2 is not None
        assert snapshot1 is not None

        # Check if the depends_on relationship exists in the raw manifest
        if "model.package.model1" in raw_manifest["nodes"]["model.package.model2"][
            "depends_on"
        ].get("nodes", []):
            # Then verify model1 is in model2's parents
            model1 = loader.get_model_by_name("model1")
            assert model1 is not None
            assert model1 in model2.parents

        # Check parent relationships for snapshot1
        if "source.package.my_source.table1" in raw_manifest["nodes"][
            "snapshot.package.snapshot1"
        ]["depends_on"].get("nodes", []):
            # Verify the source is in the snapshot's parents
            source1 = loader.get_source_by_name("table1")
            assert source1 is not None
            assert source1 in snapshot1.parents

        # Test a model with multiple parents
        # Assuming we have a model with multiple parents in the test manifest
        for node_id in raw_manifest["nodes"].keys():
            if (
                node_id.startswith("model.")
                and len(raw_manifest["nodes"][node_id]["depends_on"].get("nodes", []))
                > 1
            ):
                model_with_deps = loader.models.get(node_id)
                assert model_with_deps is not None
                # Verify all dependencies are in the parents list
                for dep_id in raw_manifest["nodes"][node_id]["depends_on"].get(
                    "nodes", []
                ):
                    # Use different variable names to avoid type issues
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

                    if dep_id.startswith(("model.", "source.", "snapshot.", "seed.")):
                        assert parent_found, f"Dependency {dep_id} should be in parents"
