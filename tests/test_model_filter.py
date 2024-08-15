"""Test model filters."""

from dbt_score.model_filter import ModelFilter, model_filter
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


def test_class_filter(model1, model2):
    """Test basic filter using class."""

    class OnlyModel1(ModelFilter):
        description = "Some description."

        def evaluate(self, model: Model) -> bool:
            return model.name == "model1"

    instance = OnlyModel1()
    assert instance.description == "Some description."
    assert instance.evaluate(model1)
    assert not instance.evaluate(model2)
