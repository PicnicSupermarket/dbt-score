"""Test rule filters."""
import pytest
from dbt_score.models import Model, Source
from dbt_score.rule_filter import RuleFilter, rule_filter


def test_basic_filter(model1, model2):
    """Test basic filter testing for a specific model."""

    @rule_filter
    def only_model1(model: Model) -> bool:
        """Some description."""
        return model.name == "model1"

    instance = only_model1()  # since the decorator returns a Type
    assert instance.description == "Some description."
    assert instance.evaluate(model1)
    assert not instance.evaluate(model2)


def test_basic_filter_with_sources(source1, source2):
    """Test basic filter testing for a specific source."""

    @rule_filter
    def only_source1(source: Source) -> bool:
        """Some description."""
        return source.name == "table1"

    instance = only_source1()  # since the decorator returns a Type
    assert instance.description == "Some description."
    assert instance.evaluate(source1)
    assert not instance.evaluate(source2)


def test_class_filter(model1, model2):
    """Test basic filter using class."""

    class OnlyModel1(RuleFilter):
        description = "Some description."

        def evaluate(self, model: Model) -> bool:  # type: ignore[override]
            return model.name == "model1"

    instance = OnlyModel1()
    assert instance.description == "Some description."
    assert instance.evaluate(model1)
    assert not instance.evaluate(model2)


def test_class_filter_with_sources(source1, source2):
    """Test basic filter using class."""

    class OnlySource1(RuleFilter):
        description = "Some description."

        def evaluate(self, source: Source) -> bool:  # type: ignore[override]
            return source.name == "table1"

    instance = OnlySource1()
    assert instance.description == "Some description."
    assert instance.evaluate(source1)
    assert not instance.evaluate(source2)


def test_missing_description_rule_filter():
    """Test missing description in filter decorator."""
    with pytest.raises(AttributeError):

        @rule_filter()
        def example_filter(model: Model) -> bool:
            return True


def test_missing_description_rule_class():
    """Test missing description in filter class."""
    with pytest.raises(AttributeError):

        class BadFilter(RuleFilter):
            """Bad example filter."""

            def evaluate(self, model: Model) -> bool:  # type: ignore[override]
                """Evaluate filter."""
                return True


def test_missing_evaluate_rule_class(model1):
    """Test missing evaluate implementation in filter class."""
    with pytest.raises(TypeError):

        class BadFilter(RuleFilter):
            """Bad example filter."""

            description = "Description of the rule."
