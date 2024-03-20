"""Test rule."""

import pytest
from dbt_score.models import Model
from dbt_score.rule import Rule, RuleViolation, Severity


def test_rule_decorator(decorator_rule, class_rule, model1, model2):
    """Test rule creation with the rule decorator and class."""
    decorator_rule_instance = decorator_rule()
    class_rule_instance = class_rule()

    def assertions(rule_instance):
        assert isinstance(rule_instance, Rule)
        assert rule_instance.severity == Severity.MEDIUM
        assert rule_instance.description == "Description of the rule."
        assert rule_instance.evaluate(model1) == RuleViolation(
            message="Model1 is a violation.")
        assert rule_instance.evaluate(model2) is None

    assertions(decorator_rule_instance)
    assertions(class_rule_instance)


def test_missing_description_rule_class(class_rule):
    """Test missing description in rule class."""
    with pytest.raises(TypeError):
        class BadRule(Rule):
            """Bad example rule."""

            def evaluate(self, model: Model) -> RuleViolation | None:
                """Evaluate model."""
                return None


def test_missing_evaluate_rule_class(class_rule, model1):
    """Test missing evaluate implementation in rule class."""
    class BadRule(Rule):
        """Bad example rule."""
        description = "Description of the rule."

    rule = BadRule()

    with pytest.raises(NotImplementedError):
        rule.evaluate(model1)

