"""This module is responsible for loading configuration."""

import logging
import tomllib
from dataclasses import dataclass, field
from typing import Any, Final

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = "pyproject.toml"


@dataclass
class RuleConfig:
    """Configuration for a rule."""

    severity: int | None = None
    params: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(rule_config: dict[str, Any]) -> "RuleConfig":
        """Create a RuleConfig from a dictionary."""
        copy = rule_config.copy()
        severity = copy.pop("severity", None)
        return RuleConfig(severity=severity, params=copy)


class Config:
    """Configuration for dbt-score."""

    _main_section: Final = "tool.dbt-score"
    _options: Final = ["rule_namespaces", "disabled_rules"]
    _rules_section: Final = f"{_main_section}.rules"

    def __init__(self) -> None:
        """Initialize the Config object."""
        self.rule_namespaces: list[str] = ["dbt_score_rules"]
        self.disabled_rules: list[str] = []
        self.rules_config: dict[str, RuleConfig] = {}

    def set_option(self, option: str, value: Any) -> None:
        """Set an option in the config."""
        setattr(self, option, value)

    def load_toml_file(self, file: str) -> None:
        """Load the options from a TOML file."""
        with open(file, "rb") as f:
            toml_data = tomllib.load(f)
            tools = toml_data.get("tool", {})
            dbt_score_config = tools.get("dbt-score", {})

            # Main configuration
            for option, value in dbt_score_config.items():
                # If value is a dictionary, it's another section
                if option in self._options and not isinstance(value, dict):
                    self.set_option(option, value)
                else:
                    logger.warning(
                        f"Option {option} in {self._main_section} not supported."
                    )

            # Rule configuration
            self.rules_config = {
                name: RuleConfig.from_dict(config)
                for name, config in dbt_score_config.get("rules", {}).items()
            }
