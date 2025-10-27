# Create rules

In order to lint and score dbt entities, `dbt-score` uses a set of rules that
are applied to each item. A rule can pass or fail when it is run. Based on the
severity of the rule, items are scored with the weighted average of the rules
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
def model_has_description(model: Model) -> RuleViolation | None:
    """A model should have a description."""
    if not model.description:
        return RuleViolation(message="Model lacks a description.")
```

The name of the function is the name of the rule and the docstring of the
function is its description. Therefore, it is important to use a
self-explanatory name for the function and document it well.

The type annotation for the rule's argument dictates whether the rule should be
applied to dbt models, sources, snapshots, seeds, exposures, or macros.

Here is the same example rule, applied to sources:

```python
from dbt_score import rule, RuleViolation, Source

@rule
def source_has_description(source: Source) -> RuleViolation | None:
   """A source should have a description."""
   if not source.description:
      return RuleViolation(message="Source lacks a description.")
```

The severity of a rule can be set using the `severity` argument:

```python
from dbt_score import rule, Severity

@rule(severity=Severity.HIGH)
```

### Using the `Rule` class

For more advanced use cases, a rule can be created by inheriting from the `Rule`
class:

```python
from dbt_score import Model, Rule, RuleViolation, Source

class ModelHasDescription(Rule):
    description = "A model should have a description."

    def evaluate(self, model: Model) -> RuleViolation | None:
        """Evaluate the rule."""
        if not model.description:
            return RuleViolation(message="Model lacks a description.")

class SourceHasDescription(Rule):
   description = "A source should have a description."

   def evaluate(self, source: Source) -> RuleViolation | None:
      """Evaluate the rule."""
      if not source.description:
         return RuleViolation(message="Source lacks a description.")
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

### Filtering rules

Custom and standard rules can be configured to have filters. Filters allow a dbt
entity to be ignored by one or multiple rules if the item doesn't satisfy the
filter criteria.

Filters are created using the same discovery mechanism and interface as custom
rules, except they do not accept parameters. Similar to Python's built-in
`filter` function, when the filter evaluation returns `True` the item should be
evaluated, otherwise it should be ignored.

```python
from dbt_score import Model, RuleFilter, rule_filter

@rule_filter
def only_schema_x(model: Model) -> bool:
    """Only applies a rule to schema X."""
    return model.schema.lower() == 'x'

class SkipSchemaY(RuleFilter):
    description = "Applies a rule to every schema but Y."
    def evaluate(self, model: Model) -> bool:
      return model.schema.lower() != 'y'
```

Filters also rely on type-annotations to dictate whether they apply to models,
sources, snapshots, seeds, or exposures:

```python
from dbt_score import RuleFilter, rule_filter, Source

@rule_filter
def only_from_source_a(source: Source) -> bool:
   """Only applies a rule to source tables from source X."""
   return source.source_name.lower() == 'a'

class SkipSourceDatabaseB(RuleFilter):
   description = "Applies a rule to every source except Database B."
   def evaluate(self, source: Source) -> bool:
      return source.database.lower() != 'b'
```

Similar to setting a rule severity, standard rules can have filters set in the
[configuration file](configuration.md/#tooldbt-scorerulesrule_namespacerule_name),
while custom rules accept the configuration file or a decorator parameter.

```python
from dbt_score import Model, rule, RuleViolation
from my_project import only_schema_x

@rule(rule_filters={only_schema_x()})
def models_in_x_follow_naming_standard(model: Model) -> RuleViolation | None:
    """Models in schema X must follow the naming standard."""
    if some_regex_fails(model.name):
        return RuleViolation("Invalid model name.")
```

### Debugging rules

When writing new rules, or investigating failing ones, you can make use of a
debug mode, which will automatically give you a debugger in case of an exception
occurring.

Run dbt-score with the debugger:

```shell
dbt-score lint --debug
# --debug and -d are equivalent
```

The debugger is the standard `pdb`, see
[its available commands](https://docs.python.org/3/library/pdb.html#debugger-commands).

Naturally, you're free to use your debugger of choice, this option exists to
enable quick debugging in any environment.
