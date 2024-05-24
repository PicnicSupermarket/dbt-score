# Create rules

In order to lint and score models, `dbt-score` uses a set of rules that are
applied to each model. A rule can pass or fail when it is run. Based on the
severity of the rule models are scored. `dbt-score` has a set of rules enabled
by default, which can be found [here](reference/rules/generic.md).

On top of the generic rules, it's possible to add your own rules. Two ways exist
to create a new rule:

1. By using the `@rule` decorator, which is the preferred/simple way.
2. By inheriting from the `Rule` class, which is more advanced and allows to
   keep state between evaluations.

### Using the `@rule` decorator

The `@rule` decorator can be used to easily create a new rule:

```python
from dbt_score import Model, rule, RuleViolation

@rule
def has_description(model: Model) -> RuleViolation | None:
    """A model should have a description."""
    if not model.description:
        return RuleViolation(message="Model lacks a description.")
```

The name of the function is the name of the rule and the docstring of the
function is its description. Therefore, it is important to use a
self-explanatory name for the function and document it well.

The severity of a rule can be set using the `severity` argument:

```python
from dbt_score import rule, Severity

@rule(severity=Severity.HIGH)
```

### Using the `Rule` class

For more advanced use cases, a rule can be created by inheriting from the `Rule`
class:

```python
from dbt_score import Model, Rule, RuleViolation

class HasDescription(Rule):
    description = "A model should have a description."

    def evaluate(self, model: Model) -> RuleViolation | None:
        """Evaluate the rule."""
        if not model.description:
            return RuleViolation(message="Model lacks a description.")
```

### Rules location

By default `dbt-score` will look for rules in the Python namespace
`dbt_score_rules`. Rules can be stored in a folder, in the root of the project
where `dbt-score` is executed. In this folder, all rules defined in `.py` files
will be automatically discovered.
