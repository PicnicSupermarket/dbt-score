"""All general rules."""

from ..manifest import Model
from ..rule import RuleViolation, Severity, rule


@rule(
    description="A model should have an owner defined.",
    hint="Define the owner of the model in the meta section.",
    severity=Severity.HIGH,
)
def has_owner(model: Model) -> RuleViolation | None:
    """A model should have an owner defined."""
    if "owner" not in model.meta:
        return RuleViolation()

    return None


@rule(description="A model should have a primary key defined.", hint="Some hint.")
def has_primary_key(model: Model) -> RuleViolation | None:
    """A model should have a primary key defined, unless it's a view."""
    if not model.config.get("materialized") == "picnic_view":
        has_pk = False
        for column in model.columns.values():
            if "primary_key" in [constraint.type for constraint in column.constraints]:
                has_pk = True
                break

        if not has_pk:
            return RuleViolation()

    return None


@rule(
    description="Primary key columns should have a uniqueness test defined.",
    hint="Some hint.",
)
def primary_key_has_uniqueness_test(model: Model) -> RuleViolation | None:
    """Primary key columns should have a uniqueness test defined."""
    columns_with_pk = []
    if not model.config.get("materialized") == "picnic_view":
        for column_name, column in model.columns.items():
            if "primary_key" in [constraint.type for constraint in column.constraints]:
                columns_with_pk.append(column_name)

        tests = (
            model.columns[columns_with_pk[0]].tests
            if len(columns_with_pk) == 1
            else model.tests
        )

        if columns_with_pk and "unique" not in [test.type for test in tests]:
            return RuleViolation()

    return None


@rule(
    description="All columns of a model should have a description.", hint="Some hint."
)
def columns_have_description(model: Model) -> RuleViolation | None:
    """All columns of a model should have a description."""
    invalid_columns = [
        column_name
        for column_name, column in model.columns.items()
        if not column.description
    ]
    if invalid_columns:
        return RuleViolation(
            message=f"The following columns lack a description: "
            f"{', '.join(invalid_columns)}."
        )

    return None


@rule(description="A model should have at least one test defined.", hint="Some hint.")
def has_test(model: Model) -> RuleViolation | None:
    """A model should have at least one model-level and one column-level test.

    This does not include singular tests, which are tests defined in a separate .sql
    file and not linked to the model in the metadata.
    """
    column_tests = []
    for column in model.columns.values():
        column_tests.extend(column.tests)

    if len(model.tests) == 0 or len(column_tests) == 0:
        return RuleViolation()

    return None
