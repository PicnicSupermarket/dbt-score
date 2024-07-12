"""Test model filters."""

from dbt_score.model_filter import model_filter
from dbt_score.models import Model


def test_basic_filter(model1, model2):
    """Test basic filter testing for a specific model."""

    @model_filter
    def only_model1(model: Model) -> bool:
        """Some description."""
        return model.name == "model1"

    instance = only_model1()  # since the decorator returns a Type
    assert instance.description == "Some description."
    assert instance.evaluate(model1)
    assert not instance.evaluate(model2)
