# Create rules

In order to lint and score models, `dbt-score` uses a set of rules that are
applied to each model. A rule can pass or fail when it is applied to a model.
Based on the severity of the rule models are scored. `dbt-score` has a set of
rules enabled by default, which can be found [here](reference/rules/generic.md).

On top of the generic rules, it's possible to add your own rules. By default
`dbt-score` will look for rules in the namespace `dbt_score_rules`.

Two ways exist to create a new rule:

1. By using the `@rule` decorator, which is the preferred/simple way.
2. By inheriting from the `Rule` class, which is more advanced.

### Using the `@rule` decorator

The `@rule` decorator can be used to easily create a new rule:

```python
@rule
def has_description(model: Model) -> RuleViolation | None:
    """A model should have a description."""
    if not model.description:
        return RuleViolation(message="Model lacks a description.")
```

The severity of a rule can be set using the `severity` argument:

```python
@rule(severity=Severity.HIGH)
```

### Using the `Rule` class

For more advanced use cases, a rule can be created by inheriting from the `Rule`
class:

```python
class HasDescription(Rule):
    description = "A model should have a description."

    def evaluate(self, model: Model) -> RuleViolation | None:
        """Evaluate the rule."""
        if not model.description:
            return RuleViolation(message="Model lacks a description.")
```

Using the rule class can be useful if the rule needs to keep state between
evaluations.
