"""Test macro rules."""

from dbt_score import Macro
from dbt_score.rules.macros import (
    macro_arguments_have_description,
    macro_has_description,
    macro_name_follows_naming_convention,
)


def test_macro_has_description(macro1, macro2):
    """Test macro_has_description rule."""
    rule = macro_has_description()
    assert rule.evaluate(macro1) is None
    assert rule.evaluate(macro2) is not None


def test_macro_arguments_have_description():
    """Test macro_arguments_have_description rule."""
    rule = macro_arguments_have_description()

    # Macro with no arguments - should pass
    macro_no_args = Macro(
        unique_id="macro.package.test",
        name="test_macro",
        description="Test",
        original_file_path="macros/test.sql",
        package_name="package",
        macro_sql="{% macro test() %}\n  SELECT 1\n{% endmacro %}",
        meta={},
        tags=[],
        arguments=[],
    )
    assert rule.evaluate(macro_no_args) is None

    # Macro with documented arguments - should pass
    macro_with_docs = Macro(
        unique_id="macro.package.test",
        name="test_macro",
        description="Test",
        original_file_path="macros/test.sql",
        package_name="package",
        macro_sql="{% macro test(arg1) %}\n  SELECT {{ arg1 }}\n{% endmacro %}",
        meta={},
        tags=[],
        arguments=[{"name": "arg1", "description": "First argument"}],
    )
    assert rule.evaluate(macro_with_docs) is None

    # Macro with undocumented arguments - should fail
    macro_no_docs = Macro(
        unique_id="macro.package.test",
        name="test_macro",
        description="Test",
        original_file_path="macros/test.sql",
        package_name="package",
        macro_sql="{% macro test(arg1) %}\n  SELECT {{ arg1 }}\n{% endmacro %}",
        meta={},
        tags=[],
        arguments=[{"name": "arg1"}],
    )
    violation = rule.evaluate(macro_no_docs)
    assert violation is not None
    assert violation.message is not None
    assert "arg1" in violation.message


def test_macro_name_follows_naming_convention():
    """Test macro_name_follows_naming_convention rule."""
    rule = macro_name_follows_naming_convention()

    # Good snake_case name - should pass
    macro_good = Macro(
        unique_id="macro.package.test",
        name="calculate_discount_rate",
        description="Test",
        original_file_path="macros/test.sql",
        package_name="package",
        macro_sql="{% macro calculate_discount_rate() %}\n  SELECT 1\n{% endmacro %}",
        meta={},
        tags=[],
    )
    assert rule.evaluate(macro_good) is None

    # CamelCase name - should fail
    macro_camel = Macro(
        unique_id="macro.package.test",
        name="CalculateDiscount",
        description="Test",
        original_file_path="macros/test.sql",
        package_name="package",
        macro_sql="{% macro CalculateDiscount() %}\n  SELECT 1\n{% endmacro %}",
        meta={},
        tags=[],
    )
    violation = rule.evaluate(macro_camel)
    assert violation is not None
    assert violation.message is not None
    assert "snake_case" in violation.message
