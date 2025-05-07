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

        model1 = loader.models["model.package.model1"]
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

        assert loader.exposures["exposure.package.exposure1"].parents == [
            loader.models["model.package.model1"]
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
