"""Generate rule documentation."""

import abc
import inspect
import textwrap

from dbt_score.config import Config
from dbt_score.rule import Rule
from dbt_score.rule_registry import RuleRegistry


class Formatter(abc.ABC):
    """A rule catalog formatter."""

    @staticmethod
    @abc.abstractmethod
    def header(title: str | None) -> str | None:
        """Return text at the top."""
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def footer() -> str | None:
        """Return text at the bottom."""
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def format_rule(rule: Rule) -> str | None:
        """Return text for a given rule."""
        raise NotImplementedError


class PlainTextFormatter(Formatter):
    """A terminal formatter."""

    @staticmethod
    def header(title: str | None) -> str | None:
        """Return text at the top."""
        return None

    @staticmethod
    def footer() -> str | None:
        """Return text at the bottom."""
        return None

    @staticmethod
    def bold(text: str) -> str:
        """Return text in bold."""
        return f"\033[1m{text}\033[0m"

    @staticmethod
    def format_rule(rule: Rule) -> str | None:
        """Return text for a given rule."""
        return f"{PlainTextFormatter.bold(rule.source())}:\n    {rule.description}\n"


class MarkdownFormatter(Formatter):
    """A formatter for MkDocs (Markdown)."""

    @staticmethod
    def header(title: str | None) -> str | None:
        """Return text at the top."""
        if title:
            return f"# {title}\n"
        return "# Rules\n"

    @staticmethod
    def footer() -> str | None:
        """Return text at the bottom."""
        return None

    @staticmethod
    def format_rule(rule: Rule) -> str | None:
        """Return text for a given rule."""
        rule_name = rule.source().split(".")[-1]

        rule_description = rule.description

        if hasattr(rule, "_orig_evaluate"):
            rule_source_code = inspect.getsource(rule._orig_evaluate)
        else:
            rule_source_code = inspect.getsource(rule.__class__)
        rule_source_code = textwrap.indent(rule_source_code, " " * 4)

        rule_configuration = f'[tool.dbt-score.rules."{rule.source()}"]\n'
        rule_configuration += f"severity = {rule.severity.value}"
        for config_key, config_default_value in rule.default_config.items():
            rule_configuration += f"\n{config_key} = {config_default_value}"

        template = f"""## `{rule_name}`

{rule_description}

??? quote  "Source code"
    ```python
{rule_source_code}
    ```

### Default configuration

```toml title="pyproject.toml"
{rule_configuration}
```
"""
        return template


def display_catalog(config: Config, title: str, format: str) -> None:
    """Print rules catalog."""
    formatter: Formatter
    if format == "terminal":
        formatter = PlainTextFormatter()
    elif format == "markdown":
        formatter = MarkdownFormatter()
    else:
        raise Exception(f"Format {format} is not valid.")

    rule_registry = RuleRegistry(config)
    rule_registry.load_all()

    header = formatter.header(title)
    if header:
        print(header)
    for rule in rule_registry.rules.values():
        rule_doc = formatter.format_rule(rule)
        if rule_doc:
            print(rule_doc)
    footer = formatter.footer()
    if footer:
        print(footer)
