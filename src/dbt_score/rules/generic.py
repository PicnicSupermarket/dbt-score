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
        return RuleViolation(
            message=f"The following columns lack a description: "
            f"{', '.join(invalid_column_names)}."
        )
