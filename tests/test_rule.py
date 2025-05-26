"""Test rule."""

import pytest
from dbt_score import (
    Exposure,
    Model,
    Rule,
    RuleViolation,
    Seed,
    Severity,
    Snapshot,
    Source,
    rule,
)
from dbt_score.rule_filter import RuleFilter, rule_filter


def test_rule_decorator_and_class(
    decorator_rule,
    decorator_rule_no_parens,
    decorator_rule_args,
    class_rule,
    model1,
    model2,
):
    """Test rule creation with the rule decorator and class."""
    decorator_rule_instance = decorator_rule()
    decorator_rule_no_parens_instance = decorator_rule_no_parens()
    decorator_rule_args_instance = decorator_rule_args()
    class_rule_instance = class_rule()

    def assertions(rule_instance):
        assert isinstance(rule_instance, Rule)
        assert rule_instance.severity == Severity.MEDIUM
        assert rule_instance.description == "Description of the rule."
        assert rule_instance.evaluate(model1) == RuleViolation(
            message="Model1 is a violation."
        )
        assert rule_instance.evaluate(model2) is None

    assertions(decorator_rule_instance)
    assertions(decorator_rule_no_parens_instance)
    assertions(decorator_rule_args_instance)
    assertions(class_rule_instance)


def test_missing_description_rule_decorator():
    """Test missing description in rule decorator."""
    with pytest.raises(AttributeError):

        @rule()
        def example_rule(model: Model) -> RuleViolation | None:
            return None


def test_missing_description_rule_class():
    """Test missing description in rule class."""
    with pytest.raises(AttributeError):

        class BadRule(Rule):
            """Bad example rule."""

            def evaluate(self, model: Model) -> RuleViolation | None:  # type: ignore[override]
                """Evaluate model."""
                return None


def test_missing_evaluate_rule_class(model1):
    """Test missing evaluate implementation in rule class."""
    with pytest.raises(TypeError):

        class BadRule(Rule):
            """Bad example rule."""

            description = "Description of the rule."


@pytest.mark.parametrize(
    "rule_fixture,expected_type",
    [
        ("decorator_rule", Model),
        ("decorator_rule_no_parens", Model),
        ("decorator_rule_args", Model),
        ("class_rule", Model),
        ("decorator_rule_source", Source),
        ("decorator_rule_no_parens_source", Source),
        ("decorator_rule_args_source", Source),
        ("class_rule_source", Source),
        ("decorator_rule_snapshot", Snapshot),
        ("decorator_rule_no_parens_snapshot", Snapshot),
        ("decorator_rule_args_snapshot", Snapshot),
        ("class_rule_snapshot", Snapshot),
        ("decorator_rule_exposure", Exposure),
        ("decorator_rule_no_parens_exposure", Exposure),
        ("decorator_rule_args_exposure", Exposure),
        ("class_rule_exposure", Exposure),
        ("decorator_rule_seed", Seed),
        ("decorator_rule_no_parens_seed", Seed),
        ("decorator_rule_args_seed", Seed),
        ("class_rule_seed", Seed),
    ],
)
def test_rule_introspects_its_resource_type(request, rule_fixture, expected_type):
    """Test that each rule is aware of the resource-type it is evaluated against."""
    rule = request.getfixturevalue(rule_fixture)
    assert rule().resource_type is expected_type


class TestRuleFilterValidation:
    """Tests that a rule filter matches resource-type to the rule it's attached to."""

    @pytest.fixture
    def source_filter_no_parens(self):
        """Example source filter with bare decorator."""

        @rule_filter
        def source_filter(source: Source) -> bool:
            """Description."""
            return False

        return source_filter()

    @pytest.fixture
    def source_filter_parens(self):
        """Example source filter with decorator and parens."""

        @rule_filter()
        def source_filter(source: Source) -> bool:
            """Description."""
            return False

        return source_filter()

    @pytest.fixture
    def source_filter_class(self):
        """Example class-based source filter."""

        class SourceFilter(RuleFilter):
            description = "Description"

            def evaluate(self, source: Source) -> bool:  # type: ignore[override]
                return False

        return SourceFilter

    @pytest.mark.parametrize(
        "rule_filter_fixture",
        ["source_filter_no_parens", "source_filter_parens", "source_filter_class"],
    )
    def test_rule_filter_must_match_resource_type_as_rule(
        self, request, rule_filter_fixture
    ):
        """Tests that rules can't be created with filters of incorrect resource-type."""
        rule_filter = request.getfixturevalue(rule_filter_fixture)

        with pytest.raises(TypeError) as excinfo:

            @rule(rule_filters={rule_filter})
            def model_always_passes(model: Model) -> RuleViolation | None:
                """Description."""
                pass

        assert "Mismatched resource_type on filter" in str(excinfo.value)
        assert "Expected Model, but got Source" in str(excinfo.value)

        with pytest.raises(TypeError):

            class ModelAlwaysPasses(Rule):
                description = "Description."
                rule_filters = frozenset([rule_filter])

                def evaluate(self, model: Model) -> RuleViolation | None:  # type: ignore[override]
                    pass

        assert "Mismatched resource_type on filter" in str(excinfo.value)
        assert "Expected Model, but got Source" in str(excinfo.value)
