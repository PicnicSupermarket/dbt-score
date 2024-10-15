"""Test rule."""

import pytest
from dbt_score import Model, Rule, RuleViolation, Severity, Source, rule


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

            def evaluate(self, model: Model) -> RuleViolation | None:
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
    ],
)
def test_rule_introspects_its_resource_type(request, rule_fixture, expected_type):
    """Test that each rule is aware of the resource-type that it can be evaluated against."""
    rule = request.getfixturevalue(rule_fixture)
    assert rule().resource_type is expected_type
