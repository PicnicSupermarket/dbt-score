"""All generic rules."""

from dbt_score import Model, RuleViolation, Severity, rule
from dbt_score.rules.filters import is_table


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
        if "```sql" not in (model.description or ""):
            return RuleViolation(
                "The model description does not include an example SQL query."
            )

@rule(rule_filters={is_table()})
def has_uniqueness_test(model: Model) -> RuleViolation | None:
    """Model has uniqueness test for primary key."""
    # ruff: noqa: C901 [too-complex]
    # ruff: noqa: PLR0912 [too-many-branches]

    # Extract PK
    pk_columns = None
    # At column level?
    for column in model.columns:
        for constraint in column.constraints:
            if constraint.type == "primary_key":
                pk_columns = [column.name]
                break
        else:
            continue
        break
    # Or at table level?
    if pk_columns is None:
        for constraint in model.constraints:
            if constraint["type"] == "primary_key":
                pk_columns = constraint["columns"]
                break

    if pk_columns is None: # No PK, no need for uniqueness test
        return None

    # Look for matching uniqueness test
    if len(pk_columns) == 1:
        for column in model.columns:
            if column.name == pk_columns[0]:
                for data_test in column.tests:
                    if data_test.type == "unique":
                        return None

    for data_test in model.tests:
        if data_test.type == "unique_combination_of_columns":
            if set(data_test.kwargs.get("combination_of_columns")) == set(pk_columns):
                return None

    return RuleViolation("There is no uniqueness test defined and matching the PK.")
