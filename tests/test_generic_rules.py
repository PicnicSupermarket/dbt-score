"""Tests for generic model rules."""

from typing import Any

import pytest

from dbt_score.models import Model
from dbt_score.rule import RuleConfig, RuleViolation
from dbt_score.rules.generic import high_fan_out_model_has_contract


def create_model(
    name: str,
    children: list[Model] | None = None,
    config: dict[str, Any] | None = None,
    language: str = "sql",
) -> Model:
    """Create a minimal model for testing."""
    return Model(
        unique_id=f"model.package.{name}",
        name=name,
        relation_name=f"db.schema.{name}",
        description="",
        original_file_path=f"models/{name}.sql",
        config=config or {},
        meta={},
        columns=[],
        package_name="package",
        database="db",
        schema="schema",
        raw_code="select 1",
        language=language,
        access="protected",
        group=None,
        children=list(children or []),
    )


def create_parent(n_children: int, **kwargs: Any) -> Model:
    """Create a model with `n_children` direct child models."""
    children = [create_model(f"child_{i}") for i in range(n_children)]
    return create_model("parent", children=children, **kwargs)


def test_high_fan_out_model_has_contract_violation():
    """A model above the threshold without a contract is a violation."""
    rule = high_fan_out_model_has_contract()
    result = rule.evaluate(create_parent(11))
    assert isinstance(result, RuleViolation)
    assert result.message == (
        "Model has 11 downstream models (> 10) but no enforced contract."
    )


def test_high_fan_out_model_has_contract_counts_transitive_models():
    """Transitive downstream models count towards the threshold."""
    grandchildren = [create_model(f"grandchild_{i}") for i in range(10)]
    child = create_model("child", children=grandchildren)
    parent = create_model("parent", children=[child])

    rule = high_fan_out_model_has_contract()
    assert isinstance(rule.evaluate(parent), RuleViolation)
    assert rule.evaluate(child) is None


def test_high_fan_out_model_has_contract_at_threshold():
    """A model at the threshold is not a violation."""
    rule = high_fan_out_model_has_contract()
    assert rule.evaluate(create_parent(10)) is None


@pytest.mark.parametrize(
    "config",
    [
        {"contract": {"enforced": True}},
        {"contract": {"enforced": True, "alias_types": False}},
    ],
)
def test_high_fan_out_model_has_contract_enforced(config):
    """A model with an enforced contract is not a violation."""
    rule = high_fan_out_model_has_contract()
    assert rule.evaluate(create_parent(11, config=config)) is None


@pytest.mark.parametrize(
    "config",
    [
        {"contract": {"enforced": False}},
        {"contract": None},
        {"contract": {}},
    ],
)
def test_high_fan_out_model_has_contract_not_enforced(config):
    """A contract that is not enforced is a violation."""
    rule = high_fan_out_model_has_contract()
    assert isinstance(rule.evaluate(create_parent(11, config=config)), RuleViolation)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"language": "python"},
        {"config": {"materialized": "ephemeral"}},
        {"config": {"materialized": "materialized_view"}},
    ],
)
def test_high_fan_out_model_has_contract_unsupported(kwargs):
    """Models that cannot have a contract are not violations."""
    rule = high_fan_out_model_has_contract()
    assert rule.evaluate(create_parent(11, **kwargs)) is None


def test_high_fan_out_model_has_contract_custom_threshold():
    """The threshold can be configured with `max_downstream_count`."""
    rule = high_fan_out_model_has_contract(
        rule_config=RuleConfig(config={"max_downstream_count": 2})
    )
    assert rule.evaluate(create_parent(2), **rule.config) is None
    result = rule.evaluate(create_parent(3), **rule.config)
    assert isinstance(result, RuleViolation)
    assert result.message == (
        "Model has 3 downstream models (> 2) but no enforced contract."
    )
