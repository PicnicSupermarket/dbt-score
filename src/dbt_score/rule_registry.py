"""Rule registry.

This module implements rule discovery.
"""

import importlib
import logging
import os
import pkgutil
import sys
from typing import Iterator, Type

from dbt_score.config import Config
from dbt_score.exceptions import DuplicatedRuleException
from dbt_score.rule import Rule, RuleConfig
from dbt_score.rule_filter import RuleFilter

logger = logging.getLogger(__name__)


class RuleRegistry:
    """A container for configured rules."""

    def __init__(self, config: Config) -> None:
        """Instantiate a rule registry."""
        self.config = config
        self._rules: dict[str, Rule] = {}
        self._rule_filters: dict[str, RuleFilter] = {}

    @property
    def rules(self) -> dict[str, Rule]:
        """Get all rules."""
        return self._rules

    @property
    def rule_filters(self) -> dict[str, RuleFilter]:
        """Get all filters."""
        return self._rule_filters

    def _walk_packages(self, namespace_name: str) -> Iterator[str]:
        """Walk packages and sub-packages recursively."""
        try:
            namespace = importlib.import_module(namespace_name)
        except ImportError:  # no custom rule in Python path
            if namespace_name != "dbt_score_rules":
                logger.warning(f"Can't import {namespace_name}.")
            return

        if not hasattr(namespace, "__path__"):
            # When called with a leaf, i.e. a module, don't attempt to iterate
            yield namespace_name
            return

        for package in pkgutil.walk_packages(
            namespace.__path__, namespace.__name__ + "."
        ):
            yield package.name

    def _load(self, namespace_name: str) -> None:
        """Load rules and filters found in a given namespace."""
        for module_name in self._walk_packages(namespace_name):
            module = importlib.import_module(module_name)
            for obj_name in dir(module):
                obj = module.__dict__[obj_name]
                if type(obj) is type and issubclass(obj, Rule) and obj is not Rule:
                    self._add_rule(obj)
                if (
                    type(obj) is type
                    and issubclass(obj, RuleFilter)
                    and obj is not RuleFilter
                ):
                    self._add_filter(obj)

    def _add_rule(self, rule: Type[Rule]) -> None:
        """Initialize and add a rule."""
        rule_name = rule.source()
        if rule_name in self._rules:
            raise DuplicatedRuleException(rule_name)
        if rule_name not in self.config.disabled_rules:
            rule_config = self.config.rules_config.get(rule_name, RuleConfig())
            self._rules[rule_name] = rule(rule_config=rule_config)

    def _add_filter(self, rule_filter: Type[RuleFilter]) -> None:
        """Initialize and add a filter."""
        filter_name = rule_filter.source()
        if filter_name in self._rule_filters:
            raise DuplicatedRuleException(filter_name)
        self._rule_filters[filter_name] = rule_filter()

    def load_all(self) -> None:
        """Load all rules, core and third-party."""
        # Add cwd to Python path
        old_sys_path = sys.path  # Save original values
        if self.config.inject_cwd_in_python_path and os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())

        for namespace in self.config.rule_namespaces:
            self._load(namespace)

        # Restore original values
        sys.path = old_sys_path

        self._load_filters_into_rules()

    def _load_filters_into_rules(self) -> None:
        """Loads RuleFilters into Rule objects.

        If the config of the rule has filter names in the `rule_filter_names` key,
        load those filters from the rule registry into the actual `rule_filters` field.
        Configuration overwrites any pre-existing filters.
        """
        for rule in self._rules.values():
            filter_names: list[str] = rule.rule_filter_names or []
            if len(filter_names) > 0:
                rule.set_filters(
                    rule_filter
                    for name, rule_filter in self.rule_filters.items()
                    if name in filter_names
                )
