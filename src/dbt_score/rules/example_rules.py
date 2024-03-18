"""All general rules."""

from dbt_score.models import Model
from dbt_score.rule import Rule, RuleViolation, rule


class ComplexRule(Rule):
    """Complex rule."""

    description = "Example of a complex rule."

    def preprocess(self) -> int:
        """Preprocessing."""
        return len(self.description)

    def evaluate(self, model: Model) -> RuleViolation | None:
        """Evaluate model."""
        x = self.preprocess()

        if x:
            return RuleViolation(str(x))
        else:
            return None


@rule()
def has_owner(model: Model) -> RuleViolation | None:
    """A model should have an owner defined."""
    if "owner" not in model.meta:
        return RuleViolation("Define the owner of the model in the meta section.")

    return None


@rule()
def has_primary_key(model: Model) -> RuleViolation | None:
    """A model should have a primary key defined, unless it's a view."""
    if not model.config.get("materialized") == "picnic_view":
        has_pk = False
        for column in model.columns:
            if "primary_key" in [constraint.type for constraint in column.constraints]:
                has_pk = True
                break

        if not has_pk:
            return RuleViolation()

    return None


@rule()
def primary_key_has_uniqueness_test(model: Model) -> RuleViolation | None:
    """Primary key columns should have a uniqueness test defined."""
    columns_with_pk = []
    if model.config.get("materialized") == "view":
        for column in model.columns:
            if "primary_key" in [constraint.type for constraint in column.constraints]:
                columns_with_pk.append(column)

        tests = columns_with_pk[0].tests if len(columns_with_pk) == 1 else model.tests

        if columns_with_pk and "unique" not in [test.type for test in tests]:
            return RuleViolation()

    return None


@rule()
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

    return None


@rule(description="A model should have at least one test defined.")
def has_test(model: Model) -> RuleViolation | None:
    """A model should have at least one model-level or column-level test defined.

    This does not include singular tests, which are tests defined in a separate .sql
    file and not linked to the model in the metadata.
    """
    column_tests = []
    for column in model.columns:
        column_tests.extend(column.tests)

    if len(model.tests) == 0 and len(column_tests) == 0:
        return RuleViolation("Define a test for the model on model- or column-level.")

    return None
