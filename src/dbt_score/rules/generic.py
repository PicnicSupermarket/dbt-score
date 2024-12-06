"""All generic rules."""

from dbt_score import Model, RuleViolation, Severity, rule


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
        max_length = 60
        message = f"Columns lack a description: {', '.join(invalid_column_names)}."
        if len(message) > max_length:
            message = f"{message[:60]}…"
        return RuleViolation(message=message)


@rule
def has_owner(model: Model) -> RuleViolation | None:
    """A model should have an owner."""
    if not model.meta.get("owner"):
        return RuleViolation(message="Model lacks an owner.")


@rule
def sql_has_reasonable_number_of_lines(
    model: Model, max_lines: int = 200
) -> RuleViolation | None:
    """The SQL query of a model should not be too long."""
    count_lines = len(model.raw_code.split("\n"))
    if count_lines > max_lines:
        return RuleViolation(
            message=f"SQL query too long: {count_lines} lines (> {max_lines})."
        )


@rule(severity=Severity.LOW)
def has_example_sql(model: Model) -> RuleViolation | None:
    """The documentation of a model should have an example query."""
    if model.language == "sql":
        if "```sql" not in model.description:
            return RuleViolation(
                "The model description does not include an example SQL query."
            )

@rule(severity=Severity.HIGH)
def has_uniqueness_test(model: Model) -> RuleViolation | None:
    """Model has uniqueness test for primary key."""
    if model.config["materialized"] == "view":
        return None

    # Single-column PK
    for column in model.columns:
        for constraint in column.constraints:
            if constraint.type == "primary_key":
                for data_test in column.tests:
                    if data_test.type == "unique":
                        break
                else:
                    return RuleViolation("Model must have uniqueness test for PK.")

    # Composite PK
    for constraint in model._raw_values[  # pylint: disable=protected-access
        "constraints"
    ]:
        if constraint["type"] == "primary_key":
            for data_test in model.tests:
                if data_test.type == "unique_combination_of_columns":
                    break
            else:
                return RuleViolation("Model must have uniqueness test for PK.")
