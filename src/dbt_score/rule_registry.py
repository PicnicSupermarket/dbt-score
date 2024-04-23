"""Rule registry.

This module implements rule discovery.
"""

import importlib
import logging
import pkgutil
from typing import Iterator, Type

from dbt_score.exceptions import DuplicatedRuleException
from dbt_score.rule import Rule

logger = logging.getLogger(__name__)

THIRD_PARTY_RULES_NAMESPACE = "dbt_score_rules"


class RuleRegistry:
    """A container for configured rules."""

    def __init__(self) -> None:
        """Instantiate a rule registry."""
        self._rules: dict[str, Type[Rule]] = {}

    @property
    def rules(self) -> dict[str, Type[Rule]]:
        """Get all rules."""
        return self._rules

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
                    self._add_rule(obj_name, obj)

    def _add_rule(self, name: str, rule: Type[Rule]) -> None:
        if name in self.rules:
            raise DuplicatedRuleException(name)
        self._rules[name] = rule

    def load_all(self) -> None:
        """Load all rules, core and third-party."""
        self._load("dbt_score.rules")
        self._load(THIRD_PARTY_RULES_NAMESPACE)
