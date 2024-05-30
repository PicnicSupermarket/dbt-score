# Generic

## `columns_have_description`

All columns of a model should have a description.

??? quote "Source code" ```python @rule def columns_have_description(model:
Model) -> RuleViolation | None: """All columns of a model should have a
description.""" invalid_column_names = [ column.name for column in model.columns
if not column.description ] if invalid_column_names: max_length = 60 message =
f"Columns lack a description: {', '.join(invalid_column_names)}." if
len(message) > max_length: message = f"{message[:60]}…" return
RuleViolation(message=message)

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."dbt_score.rules.generic.columns_have_description"]
severity = 2
```

## `has_description`

A model should have a description.

??? quote "Source code" ```python @rule def has_description(model: Model) ->
RuleViolation | None: """A model should have a description.""" if not
model.description: return RuleViolation(message="Model lacks a description.")

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."dbt_score.rules.generic.has_description"]
severity = 2
```

## `has_owner`

A model should have an owner.

??? quote "Source code" ```python @rule def has_owner(model: Model) ->
RuleViolation | None: """A model should have an owner.""" if not
model.meta.get("owner"): return RuleViolation(message="Model lacks an owner.")

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."dbt_score.rules.generic.has_owner"]
severity = 2
```

## `public_model_has_example_sql`

The documentation of a public model should have an example query.

??? quote "Source code"
`python     @rule(severity=Severity.LOW)     def public_model_has_example_sql(model: Model) -> RuleViolation | None:         """The documentation of a public model should have an example query."""         if model.language == "sql" and model.access == "public":             if "`sql"
not in model.description: return RuleViolation( "The model description does not
include an example SQL query." )

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."dbt_score.rules.generic.public_model_has_example_sql"]
severity = 1
```

## `sql_has_reasonable_number_of_lines`

The SQL query of a model should not be too long.

??? quote "Source code" ```python @rule def sql_has_reasonable_number_of_lines(
model: Model, max_lines: int = 200 ) -> RuleViolation | None: """The SQL query
of a model should not be too long.""" count_lines =
len(model.raw_code.split("\n")) if count_lines > max_lines: return
RuleViolation( message=f"SQL query too long: {count_lines} lines (>
{max_lines})." )

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."dbt_score.rules.generic.sql_has_reasonable_number_of_lines"]
severity = 1
max_lines = 200
```
