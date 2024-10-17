"""Test model filters."""
import pytest
from dbt_score.model_filter import ModelFilter, model_filter
from dbt_score.models import Model, Source


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


def test_basic_filter_with_sources(source1, source2):
    """Test basic filter testing for a specific model."""

    @model_filter
    def only_source1(source: Source) -> bool:
        """Some description."""
        return source.name == "table1"

    instance = only_source1()  # since the decorator returns a Type
    assert instance.description == "Some description."
    assert instance.evaluate(source1)
    assert not instance.evaluate(source2)


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


def test_class_filter_with_sources(source1, source2):
    """Test basic filter using class."""

    class OnlySource1(ModelFilter):
        description = "Some description."

        def evaluate(self, source: Source) -> bool:
            return source.name == "table1"

    instance = OnlySource1()
    assert instance.description == "Some description."
    assert instance.evaluate(source1)
    assert not instance.evaluate(source2)


def test_missing_description_rule_filter():
    """Test missing description in filter decorator."""
    with pytest.raises(AttributeError):

        @model_filter()
        def example_filter(model: Model) -> bool:
            return True


def test_missing_description_rule_class():
    """Test missing description in filter class."""
    with pytest.raises(AttributeError):

        class BadFilter(ModelFilter):
            """Bad example filter."""

            def evaluate(self, model: Model) -> bool:
                """Evaluate filter."""
                return True


def test_missing_evaluate_rule_class(model1):
    """Test missing evaluate implementation in filter class."""
    with pytest.raises(TypeError):

        class BadFilter(ModelFilter):
            """Bad example filter."""

            description = "Description of the rule."
