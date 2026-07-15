"""Unit tests for the rule catalog."""

import pytest

from dbt_score.rule_catalog import (
    MarkdownFormatter,
    display_catalog,
)


def test_rule_catalog_terminal(capsys, default_config):
    """Test rule catalog with the terminal formatter."""
    default_config.overload({"rule_namespaces": ["tests.rules"]})
    display_catalog(default_config, "Doc for tests.rules", "terminal")
    stdout = capsys.readouterr().out
    assert (
        stdout
        == """\x1b[1mtests.rules.nested.example.rule_test_nested_example\x1b[0m:
    An example rule.

\x1b[1mtests.rules.rules.rule_test_example\x1b[0m:
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

## `rule_test_example`

An example rule.

??? quote  "Source code"
    ```python
    @rule(rule_filters={skip_schemaX()})
    def rule_test_example(model: Model) -> RuleViolation | None:
        \"""An example rule.\"""

    ```

### Default configuration

```toml title="pyproject.toml"
[tool.dbt-score.rules."tests.rules.rules.rule_test_example"]
severity = 2
```

"""
    )


def test_rule_catalog_markdown_default_header(capsys, default_config):
    """The markdown formatter falls back to a default header without a title."""
    default_config.overload({"rule_namespaces": ["tests.rules"]})
    display_catalog(default_config, None, "markdown")
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Rules\n")


def test_rule_catalog_invalid_format(default_config):
    """An invalid format raises an exception."""
    with pytest.raises(Exception, match=r"Format invalid is not valid."):
        display_catalog(default_config, None, "invalid")


def test_rule_catalog_markdown_class_rule(default_config, class_rule):
    """The markdown formatter renders class-based rules with their source."""
    doc = MarkdownFormatter.format_rule(class_rule())
    assert doc is not None
    assert "## `ExampleRule`" in doc
    assert "class ExampleRule" in doc


def test_rule_catalog_markdown_default_config(default_config, rule_with_config):
    """The markdown formatter renders default configuration values."""
    doc = MarkdownFormatter.format_rule(rule_with_config())
    assert doc is not None
    assert "model_name = model1" in doc
