"""Test model filters."""

from dbt_score.model_filter import model_filter, ModelFilter
from dbt_score.models import Model


def test_basic_filter(model1, model2):
    """Test basic filter testing for a specific model."""
    @model_filter
    def only_model1(model: Model) -> bool:
        """Some description."""
        return model.name == "model1"

    assert only_model1.description == "Some description."
    assert only_model1.evaluate(only_model1, model1)
    assert not only_model1.evaluate(only_model1, model2)
