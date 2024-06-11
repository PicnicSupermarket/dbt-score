# Create rules

In order to lint and score models, `dbt-score` uses a set of rules that are
applied to each model. A rule can pass or fail when it is run. Based on the
severity of the rule, models are scored with the weighted average of the rules
results. Note that `dbt-score` comes bundled with a
[set of default rules](rules/generic.md).

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
`dbt_score_rules`. Rules can be stored anywhere in the Python path under the
`dbt_score_rules` namespace. In many cases, having such a folder in the dbt
project from where you invoke dbt and dbt-score will work. In this folder, all
rules defined in `.py` files will be automatically discovered. By default, the
current working directory is injected in the Python path.

If nested folders are used, e.g. `dbt_score_rules/generic_rules/rules.py`, an
`__init__.py` file needs to be present in the nested folder to make it
discoverable.

### Configurable rules

It's possible to create rules that can be
[configured with parameters](configuration.md/#tooldbt-scorerulesrule_namespacerule_name)
. In order to create a configurable rule, the evaluation function of the rule
should have additional input parameters with a default value defined. In the
example below, the rule has a `max_lines` parameter with a default value of 200,
which can be configured in the `pyproject.toml` file.

```python
from dbt_score import Model, rule, RuleViolation

@rule
def sql_has_reasonable_number_of_lines(model: Model, max_lines: int = 200) -> RuleViolation | None:
    """The SQL query of a model should not be too long."""
    count_lines = len(model.raw_code.split("\n"))
    if count_lines > max_lines:
        return RuleViolation(
            message=f"SQL query too long: {count_lines} lines (> {max_lines})."
        )
```
