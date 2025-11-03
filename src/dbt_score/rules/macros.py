"""Rules for dbt macros."""

import re

from dbt_score import Macro, RuleViolation, rule


@rule
def macro_has_description(macro: Macro) -> RuleViolation | None:
    """A macro should have a description.

    Macros are reusable code that should be well-documented so other developers
    can understand their purpose and usage.
    """
    if not macro.description:
        return RuleViolation(message="Macro lacks a description.")


@rule
def macro_arguments_have_description(macro: Macro) -> RuleViolation | None:
    """All macro arguments should have a description.

    From dbt Core v1.10+, macro arguments can be documented. This helps users
    understand what parameters the macro expects and how to use them correctly.
    """
    if not macro.arguments:
        return None

    invalid_args = [
        arg.get("name", "unknown")
        for arg in macro.arguments
        if not arg.get("description")
    ]
    if invalid_args:
        max_length = 60
        message = f"Arguments lack a description: {', '.join(invalid_args)}."
        if len(message) > max_length:
            message = f"{message[:max_length]}…"
        return RuleViolation(message=message)


@rule
def macro_name_follows_naming_convention(macro: Macro) -> RuleViolation | None:
    """A macro name should use snake_case naming convention.

    Consistent naming conventions improve code readability and maintainability.
    Macro names should use lowercase letters with underscores.
    """
    # Check if name follows snake_case: lowercase letters, numbers, and underscores only
    if not re.match(r"^[a-z0-9_]+$", macro.name):
        return RuleViolation(
            message="Macro name should use snake_case (lowercase with underscores)."
        )
