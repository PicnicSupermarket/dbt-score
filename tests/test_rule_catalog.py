"""Unit tests for the rule catalog."""

from dbt_score.rule_catalog import display_catalog


def test_rule_catalog_terminal(capsys, default_config):
    """Test rule catalog with the terminal formatter."""
    default_config.overload({"rule_namespaces": ["tests.rules"]})
    display_catalog(default_config, "Doc for tests.rules", "terminal")
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """\x1B[1mtests.rules.example.rule_test_example\x1B[0m:
    An example rule.

\x1B[1mtests.rules.nested.example.rule_test_nested_example\x1B[0m:
    An example rule.

"""
    )


def test_rule_catalog_markdown(capsys, default_config):
    """Test rule catalog with the markdown formatter."""
    default_config.overload({"rule_namespaces": ["tests.rules"]})
    display_catalog(default_config, "Doc for tests.rules", "markdown")
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """# Doc for tests.rules

## `rule_test_example`

An example rule.

??? quote  "Source code"
    ```python
    @rule()
    def rule_test_example(model: Model) -> RuleViolation | None:
        \"""An example rule.\"""

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."tests.rules.example.rule_test_example"]
severity = 2
```

## `rule_test_nested_example`

An example rule.

??? quote  "Source code"
    ```python
    @rule
    def rule_test_nested_example(model: Model) -> RuleViolation | None:
        \"""An example rule.\"""

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."tests.rules.nested.example.rule_test_nested_example"]
severity = 2
```

"""
    )
