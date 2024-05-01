"""Rule registry.

This module implements rule discovery.
"""

import importlib
import logging
import pkgutil
from typing import Iterator, Type

from dbt_score.config_parser import DbtScoreConfig, RuleConfig
from dbt_score.exceptions import DuplicatedRuleException
from dbt_score.rule import Rule

logger = logging.getLogger(__name__)


class RuleRegistry:
    """A container for configured rules."""

    def __init__(self, config: DbtScoreConfig) -> None:
        """Instantiate a rule registry."""
        self.config = config
        self._rules: dict[str, Type[Rule]] = {}
        self._initialized_rules: dict[str, Rule] = {}

    def init_rules(self) -> None:
        """Initialize rules."""
        for rule_name, rule_class in self._rules.items():
            rule_config = self.config.rules_config.get(rule_name,
                                                       RuleConfig())
            self._initialized_rules[rule_name] = rule_class(
                rule_config=rule_config)

    @property
    def rules(self) -> dict[str, Rule]:
        """Get all rules."""
        return self._initialized_rules

    def _walk_packages(self, namespace_name: str) -> Iterator[str]:
        """Walk packages and sub-packages recursively."""
        try:
            namespace = importlib.import_module(namespace_name)
        except ImportError:  # no custom rule in Python path
            return

        def onerror(module_name: str) -> None:
            logger.warning(f"Failed to import {module_name}.")

        for package in pkgutil.walk_packages(namespace.__path__, onerror=onerror):
            yield f"{namespace_name}.{package.name}"
            if package.ispkg:
                yield from self._walk_packages(f"{namespace_name}.{package.name}")

    def _load(self, namespace_name: str) -> None:
        """Load rules found in a given namespace."""
        for module_name in self._walk_packages(namespace_name):
            module = importlib.import_module(module_name)
            for obj_name in dir(module):
                obj = module.__dict__[obj_name]
                if type(obj) is type and issubclass(obj, Rule) and obj is not Rule:
                    self._add_rule(f"{module_name}.{obj_name}", obj)

    def _add_rule(self, name: str, rule: Type[Rule]) -> None:
        """Add a rule."""
        if name in self._rules:
            raise DuplicatedRuleException(name)
        if name not in self.config.disabled_rules:
            self._rules[name] = rule

    def load_all(self) -> None:
        """Load all rules, core and third-party."""
        self._load("dbt_score.rules")
        for namespace in self.config.rule_namespaces:
            self._load(namespace)
        self.init_rules()
