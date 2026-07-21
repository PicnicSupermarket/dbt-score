"""Tests for generic rules."""

from dbt_score.models import Column, Constraint
from dbt_score.models import Test as DbtTest
from dbt_score.rule import RuleViolation
from dbt_score.rules.generic import (
    columns_have_description,
    has_description,
    has_example_sql,
    has_no_unused_is_incremental,
    has_owner,
    has_uniqueness_test,
    single_column_uniqueness_at_column_level,
    single_pk_defined_at_column_level,
    snapshot_has_strategy,
    snapshot_has_unique_key,
    sql_has_reasonable_number_of_lines,
)

# Snapshot rules


def test_snapshot_has_unique_key(snapshot1):
    """Test snapshot_has_unique_key rule."""
    rule = snapshot_has_unique_key()
    assert rule.evaluate(snapshot1) is None

    snapshot1.config["unique_key"] = None
    assert isinstance(rule.evaluate(snapshot1), RuleViolation)


def test_snapshot_has_strategy(snapshot1):
    """Test snapshot_has_strategy rule."""
    rule = snapshot_has_strategy()
    assert rule.evaluate(snapshot1) is None

    snapshot1.config["strategy"] = None
    assert isinstance(rule.evaluate(snapshot1), RuleViolation)


# Model description rules


def test_has_description(model1, model2):
    """Test has_description rule."""
    rule = has_description()
    # model1 has no description, model2 has one.
    assert isinstance(rule.evaluate(model1), RuleViolation)
    assert rule.evaluate(model2) is None


def test_columns_have_description(model1):
    """Test columns_have_description rule."""
    rule = columns_have_description()
    # model1's single column has a description.
    assert rule.evaluate(model1) is None

    model1.columns.append(Column(name="no_desc", description=""))
    result = rule.evaluate(model1)
    assert isinstance(result, RuleViolation)
    assert result.message is not None
    assert "no_desc" in result.message


def test_columns_have_description_message_truncated(model1):
    """Test that a long list of columns produces a truncated message."""
    rule = columns_have_description()
    for i in range(20):
        model1.columns.append(Column(name=f"undocumented_column_{i}", description=""))
    result = rule.evaluate(model1)
    assert isinstance(result, RuleViolation)
    assert result.message is not None
    assert result.message.endswith("…")


def test_has_owner(model1):
    """Test has_owner rule."""
    rule = has_owner()
    assert isinstance(rule.evaluate(model1), RuleViolation)

    model1.meta["owner"] = "Data Team"
    assert rule.evaluate(model1) is None


# SQL rules


def test_sql_has_reasonable_number_of_lines(model1):
    """Test sql_has_reasonable_number_of_lines rule."""
    rule = sql_has_reasonable_number_of_lines()
    model1.raw_code = "\n".join(["select 1"] * 10)
    assert rule.evaluate(model1) is None

    model1.raw_code = "\n".join(["select 1"] * 201)
    result = rule.evaluate(model1)
    assert isinstance(result, RuleViolation)
    assert result.message is not None
    assert "201" in result.message


def test_has_example_sql(model1, model2):
    """Test has_example_sql rule."""
    rule = has_example_sql()
    # model1 (sql) has no example query in its (empty) description.
    assert isinstance(rule.evaluate(model1), RuleViolation)
    # model2 (sql) has a ```sql block in its description.
    assert rule.evaluate(model2) is None


def test_has_example_sql_non_sql_language(model1):
    """A non-sql model is exempt from the example SQL rule."""
    rule = has_example_sql()
    model1.language = "python"
    assert rule.evaluate(model1) is None


# Constraint / uniqueness rules


def test_single_pk_defined_at_column_level(model1):
    """Test single_pk_defined_at_column_level rule."""
    rule = single_pk_defined_at_column_level()
    # No constraints -> no violation.
    assert rule.evaluate(model1) is None

    # Composite PK (2 columns) -> no violation.
    model1.constraints = [Constraint(type="primary_key", columns=["a", "b"])]
    assert rule.evaluate(model1) is None

    # Single-column PK at model level (preceded by an unrelated constraint) ->
    # violation.
    model1.constraints = [
        Constraint(type="foreign_key", columns=["fk"]),
        Constraint(type="primary_key", columns=["a"]),
    ]
    assert isinstance(rule.evaluate(model1), RuleViolation)


def test_single_column_uniqueness_at_column_level(model1):
    """Test single_column_uniqueness_at_column_level rule."""
    rule = single_column_uniqueness_at_column_level()
    # No tests -> no violation.
    assert rule.evaluate(model1) is None

    # Multi-column uniqueness test -> no violation.
    model1.tests = [
        DbtTest(
            name="t",
            type="unique_combination_of_columns",
            kwargs={"combination_of_columns": ["a", "b"]},
        )
    ]
    assert rule.evaluate(model1) is None

    # Single-column uniqueness test (preceded by an unrelated test) -> violation.
    model1.tests = [
        DbtTest(name="t0", type="not_null"),
        DbtTest(
            name="t",
            type="unique_combination_of_columns",
            kwargs={"combination_of_columns": ["a"]},
        ),
    ]
    assert isinstance(rule.evaluate(model1), RuleViolation)


def test_has_uniqueness_test_single_column_pk(model1):
    """Test has_uniqueness_test rule for single-column PK."""
    rule = has_uniqueness_test()

    # Single-column PK with a unique test (preceded by unrelated ones) -> no
    # violation.
    model1.columns = [
        Column(
            name="id",
            description="",
            constraints=[
                Constraint(type="not_null"),
                Constraint(type="primary_key"),
            ],
            tests=[
                DbtTest(name="t0", type="not_null"),
                DbtTest(name="t", type="unique"),
            ],
        )
    ]
    assert rule.evaluate(model1) is None

    # Single-column PK without a unique test -> violation.
    model1.columns = [
        Column(
            name="id",
            description="",
            constraints=[Constraint(type="primary_key")],
            tests=[DbtTest(name="t0", type="not_null")],
        )
    ]
    assert isinstance(rule.evaluate(model1), RuleViolation)


def test_has_uniqueness_test_no_pk(model1):
    """A model without any PK does not require a uniqueness test."""
    rule = has_uniqueness_test()
    model1.columns = [Column(name="id", description="")]
    model1.constraints = []
    model1.tests = []
    assert rule.evaluate(model1) is None


def test_has_uniqueness_test_composite_pk(model1):
    """Test has_uniqueness_test rule for composite PK."""
    rule = has_uniqueness_test()
    model1.columns = [
        Column(name="a", description=""),
        Column(name="b", description=""),
    ]
    model1.constraints = [
        Constraint(type="foreign_key", columns=["fk"]),
        Constraint(type="primary_key", columns=["a", "b"]),
    ]

    # Matching combination test (preceded by unrelated + non-matching tests) ->
    # no violation.
    model1.tests = [
        DbtTest(name="t0", type="not_null"),
        DbtTest(
            name="t",
            type="unique_combination_of_columns",
            kwargs={"combination_of_columns": ["a", "b"]},
        ),
    ]
    assert rule.evaluate(model1) is None

    # Only a non-matching combination test -> violation.
    model1.tests = [
        DbtTest(
            name="t",
            type="unique_combination_of_columns",
            kwargs={"combination_of_columns": ["a"]},
        )
    ]
    assert isinstance(rule.evaluate(model1), RuleViolation)


# Incremental rule


def test_has_no_unused_is_incremental(model1):
    """Test has_no_unused_is_incremental rule."""
    rule = has_no_unused_is_incremental()

    # Non-incremental model without is_incremental() -> no violation.
    model1.config["materialized"] = "table"
    model1.raw_code = "select 1"
    assert rule.evaluate(model1) is None

    # Incremental model using is_incremental() -> no violation.
    model1.config["materialized"] = "incremental"
    model1.raw_code = "select 1 {% if is_incremental() %}where 1=1{% endif %}"
    assert rule.evaluate(model1) is None

    # Non-incremental model using is_incremental() -> violation.
    model1.config["materialized"] = "table"
    assert isinstance(rule.evaluate(model1), RuleViolation)
