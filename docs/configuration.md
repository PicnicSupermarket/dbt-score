# Configuration

`dbt-score` can be configured through a `pyproject.toml` file or via the command
line.

## pyproject.toml

It is recommended to place the file in the root of your dbt project. `dbt-score`
will look for `pyproject.toml` in the directory from which it is run and its
parent directories.

An example of a `pyproject.toml` file to configure `dbt-score` can be found
below:

```toml
[tool.dbt-score]
rule_namespaces = ["dbt_score.rules", "dbt_score_rules", "custom_rules"]
disabled_rules = ["dbt_score.rules.generic.columns_have_description"]
inject_cwd_in_python_path = true
fail_project_under = 7.5
fail_any_item_under = 8.0

[tool.dbt-score.badges]
first.threshold = 10.0
first.icon = "🥇"
second.threshold = 8.0
second.icon = "🥈"
third.threshold = 6.0
third.icon = "🥉"
wip.icon = "🏗️"

[tool.dbt-score.rules."dbt_score.rules.generic.sql_has_reasonable_number_of_lines"]
severity = 1
max_lines = 300
```

### Configuration options

The following options can be set in the `pyproject.toml` file:

#### Main configuration

```toml
[tool.dbt-score]
```

- `rule_namespaces`: A list of Python namespaces to search for rules. The
  default is `["dbt_score.rules", "dbt_score_rules"]`. Be aware when overriding
  this setting, that the default rules are in `dbt_score.rules` and are disabled
  if not included here.
- `disabled_rules`: A list of rules to disable.
- `fail_project_under` (default: `5.0`): If the project score is below this
  value the command will fail with return code 1.
- `fail_any_item_under` (default: `5.0`): If any entity scores below this value
  the command will fail with return code 1.

#### Badges configuration

```toml
[tool.dbt-score.badges]
```

Four badges can be configured: `first`, `second`, `third` and `wip`. Each badge
can be configured with the following option:

- `icon`: The icon to use for the badge. A string that will be displayed in the
  output, e.g. `🥇`.

All badges except `wip` can be configured with the following option:

- `threshold`: The threshold for the badge. A decimal number between `0.0` and
  `10.0` that will be used to compare to the score. The threshold is the minimum
  score required for a model or source to be rewarded with a certain badge.

The default values can be found in the
[BadgeConfig](reference/config.md#dbt_score.config.BadgeConfig).

#### Rule configuration

```toml
[tool.dbt-score.rules."rule_namespace.rule_name"]
```

Every rule can be configured with the following option:

- `severity`: The severity of the rule. Rules have a default severity and can be
  overridden. It's an integer with a minimum value of 1 and a maximum value
  of 4.
- `rule_filter_names`: Filters used by the rule. Takes a list of names that can
  be found in the same namespace as the rules (see
  [Package rules](package_rules.md)).

  Example: the generic rule `has_example_sql` shall apply only to models
  materializing a table.

  ```toml
  [tool.dbt-score.rules."dbt_score.rules.generic.has_example_sql"]
  rule_filter_names=["dbt_score.rules.filters.is_table"]
  ```

Some rules have additional configuration options, e.g.
[sql_has_reasonable_number_of_lines](rules/generic.md#sql_has_reasonable_number_of_lines).
Depending on the rule, the options will have different names, types and default
values. In the case of the
[sql_has_reasonable_number_of_lines](rules/generic.md#sql_has_reasonable_number_of_lines),
the `max_lines` option can be configured.

## Command line

Many configuration options can also be set via the command line. To understand
how to configure `dbt-score` from the command line:

```bash
dbt-score lint --help
```
