# Package rules

`dbt-score` is able to search for rules in Python packages.

The default namespaces which are searched are:

- `dbt_score.rules`: This namespace contains the core rules, i.e. those packaged
  within `dbt-score`.
- `dbt_score_rules`: This implicit namespace package can be used for any custom
  rule, either implemented by 3rd party packages or by yourself.

Additionally, `dbt-score`
[can be configured to search for rules in other namespaces](configuration.md/#main-configuration).

## Packaging for a single project

If you want to write custom rules applicable for your project only, it is
recommended to bundle them directly within your dbt project.

The only requirement for `dbt-score` to discover your custom rules is for those
rules to be present and importable in your Python environment, which might vary
depending on the way you use Python and virtual environments.

The following project structure is usually observed:

```
my-dbt-project/
├─ dbt_score_rules/
│  ├─ my_project_rules.py
├─ dbt_project.yml
├─ models/
├─ ...
```

For your convenience, `dbt-score` will inject the current working directory in
the Python path, making `dbt_score_rules` discoverable here without any further
configuration.

## Packaging for multiple projects

If you want to write custom rules which apply to multiple dbt projects within an
organization, or even to be distributed to the public, the best way is to
package them in a Python wheel.

The only thing the wheel needs to do is to expose modules within a top-level
`dbt_score_rules` (or any other namespace, as long as projects are configured to
read from such an additional namespace).

To avoid naming conflicts within the `dbt_score_rules` namespace, it is
recommended to pick module names which match either an organization, or a
specific project. For example, an hypothetical `dbtviz` project which makes use
of dbt's `meta` to describe visualizations associated to models could have rules
for this metadata saved in `dbt_score_rules.dbtviz`.

## Debugging

You can verify the list of rules discovered and configured by `dbt-score` by
running:

```shell
dbt-score list
dbt-score list --namespace dbt_score_rules.dbtviz  # filter by a given namespace
```

If your custom rules are not present, try to open a Python shell and import
them:

```python
import dbt_score_rules.dbtviz
```

If it doesn't succeed, it means the rules are not properly installed or not
within the Python path.
