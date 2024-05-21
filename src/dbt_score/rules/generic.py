"""All generic rules."""

from dbt_score import Model, RuleViolation, rule


@rule
def has_description(model: Model) -> RuleViolation | None:
    """A model should have a description."""
    if not model.description:
        return RuleViolation(message="Model lacks a description.")


@rule
def columns_have_description(model: Model) -> RuleViolation | None:
    """All columns of a model should have a description."""
    invalid_column_names = [
        column.name for column in model.columns if not column.description
    ]
    if invalid_column_names:
        message = f"Columns lack a description: {', '.join(invalid_column_names)}."
        if len(message) > 60:
            message = f"{message[:60]}…"
        return RuleViolation(message=message[:90])


@rule
def has_owner(model: Model) -> RuleViolation | None:
    """A model should have an owner."""
    if not model.meta.get("owner"):
        return RuleViolation(message="Model lacks an owner.")


@rule
def sql_has_reasonable_size(model: Model, max_lines: int = 200) -> RuleViolation | None:
    """The SQL query of a model should not be too long."""
    count_lines = len(model.raw_code.split("\n"))
    if count_lines > max_lines:
        return RuleViolation(
            message=f"SQL query too long: {count_lines} lines (> {max_lines})."
        )
