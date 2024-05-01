"""Test rule."""

import pytest
from dbt_score.models import Model
from dbt_score.rule import Rule, RuleViolation, Severity, rule


def test_rule_decorator_and_class(
    decorator_rule,
    decorator_rule_no_parens,
    decorator_rule_args,
    class_rule,
    model1,
    model2,
    default_rule_config,
):
    """Test rule creation with the rule decorator and class."""
    decorator_rule_instance = decorator_rule(default_rule_config)
    decorator_rule_no_parens_instance = decorator_rule_no_parens(default_rule_config)
    decorator_rule_args_instance = decorator_rule_args(default_rule_config)
    class_rule_instance = class_rule(default_rule_config)

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


def test_missing_evaluate_rule_class(model1, default_rule_config):
    """Test missing evaluate implementation in rule class."""

    class BadRule(Rule):
        """Bad example rule."""

        description = "Description of the rule."

    rule = BadRule(rule_config=default_rule_config)

    with pytest.raises(NotImplementedError):
        rule.evaluate(model1)
