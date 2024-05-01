"""This module is responsible for parsing the config file."""

import configparser
import json
import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar

logger = logging.getLogger(__name__)

CONFIG_FILE = "pyproject.toml"


@dataclass
class RuleConfig:
    """Rule config."""
    severity: int | None = None
    description: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(rule_config: dict[str, Any]) -> "RuleConfig":
        """Create a RuleConfig from a dictionary."""
        severity = rule_config.pop("severity", None)
        description = rule_config.pop("description", None)

        return RuleConfig(severity=severity, description=description,
                          params=rule_config)


class DbtScoreConfig:
    """Dbt score config."""

    _main_section = "tool.dbt-score"
    _options: ClassVar[list[str]] = ["rule_namespaces", "disabled_rules"]
    _rules_section = f"{_main_section}.rules"

    def __init__(self) -> None:
        """Initialize the DbtScoreConfig object."""
        self.rule_namespaces: list[str] = ["dbt_score_rules"]
        self.disabled_rules: list[str] = []
        self.rules_config: dict[str, RuleConfig] = {}

    def set_option(self, option: str, value: Any) -> None:
        """Set an option in the config."""
        setattr(self, option, value)

    def load_toml_file(self, file: str = CONFIG_FILE) -> None:
        """Load the options from a TOML file."""
        config = configparser.ConfigParser()
        config.read(file)

        # Main configuration
        if config.has_section(self._main_section):
            for option in config.options(self._main_section):
                if option in self._options:
                    self.set_option(option,
                                    json.loads(config.get(self._main_section, option)))
                else:
                    logger.warning(
                        f"Option {option} in {self._main_section} not supported.")

        # Rule configuration
        rules_sections = list(
            filter(lambda section: section.startswith(self._rules_section),
                   config.sections()))

        for rule_section in rules_sections:
            rule_name = rule_section.replace(f"{self._rules_section}.", "")
            rule_config = {param: json.loads(val) for param, val in
                           config.items(rule_section)}
            self.rules_config[rule_name] = RuleConfig.from_dict(rule_config)
