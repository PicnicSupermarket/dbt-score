"""Test models."""

from copy import deepcopy
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
        assert loader.models[0].tests[0].name == "test2"
        assert loader.models[0].tests[1].name == "test4"
        assert loader.models[0].columns[0].tests[0].name == "test1"

        assert len(loader.sources) == len(
            [
                source
                for source in raw_manifest["sources"].values()
                if source["package_name"] == raw_manifest["metadata"]["project_name"]
            ]
        )
        assert loader.sources[0].tests[0].name == "source_test1"

        # models in `parents` / `children` do not themselves have `parents`
        # or `children` populated, so we need to compare against an instance
        # with those removed
        _models = []
        for model in loader.models:
            _model = deepcopy(model)
            _model.parents = []
            _model.children = []
            _models.append(_model)
        _sources = []
        for source in loader.sources:
            _source = deepcopy(source)
            _source.children = []
            _sources.append(_source)
        _snapshots = []
        for snapshot in loader.snapshots:
            _snapshot = deepcopy(snapshot)
            _snapshot.parents = []
            _snapshot.children = []
            _snapshots.append(_snapshot)

        assert loader.snapshots[0].parents == [_models[0]]
        assert loader.snapshots[0].children == []
        assert loader.snapshots[1].children == [_models[1]]
        assert loader.models[0].parents == [_models[1], _sources[0]]
        assert loader.models[1].parents == [_snapshots[1]]
        assert loader.sources[0].children == [_snapshots[1], _models[0]]
        assert loader.models[0].children == [_snapshots[0]]
        assert loader.models[1].children == [_models[0]]
        assert loader.sources[1].children == []


@patch("dbt_score.models.Path.read_text")
def test_manifest_select_models_simple(mock_read_text, raw_manifest):
    """Test a simple selection in a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["model1"])

    assert [x.name for x in manifest_loader.models] == ["model1"]


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_select_models_dbt_ls(mock_dbt_ls, mock_read_text, raw_manifest):
    """Test a complex selection in a manifest, which uses dbt ls."""
    mock_dbt_ls.return_value = ["model1"]
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["+model1"])

    assert [x.name for x in manifest_loader.models] == ["model1"]
    mock_dbt_ls.assert_called_once_with(["+model1"])


@patch("dbt_score.models.Path.read_text")
@patch("dbt_score.models.dbt_ls")
def test_manifest_no_model(mock_dbt_ls, mock_read_text, raw_manifest, caplog):
    """Test the lack of model in a manifest."""
    with patch("dbt_score.models.json.loads", return_value=raw_manifest):
        manifest_loader = ManifestLoader(Path("some.json"), select=["non_existing"])

    assert len(manifest_loader.models) == 0
    assert "Nothing to evaluate!" in caplog.text
