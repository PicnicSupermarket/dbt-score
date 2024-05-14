"""This module is responsible for loading configuration."""

import logging
import tomllib
from pathlib import Path
from typing import Any, Final

from dbt_score.rule import RuleConfig

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = "pyproject.toml"


class Config:
    """Configuration for dbt-score."""

    _main_section: Final[str] = "tool.dbt-score"
    _options: Final[list[str]] = ["rule_namespaces", "disabled_rules"]
    _rules_section: Final[str] = f"{_main_section}.rules"

    def __init__(self) -> None:
        """Initialize the Config object."""
        self.rule_namespaces: list[str] = ["dbt_score_rules"]
        self.disabled_rules: list[str] = []
        self.rules_config: dict[str, RuleConfig] = {}
        self.config_file: Path | None = None

    def set_option(self, option: str, value: Any) -> None:
        """Set an option in the config."""
        setattr(self, option, value)

    def _load_toml_file(self, file: str) -> None:
        """Load the options from a TOML file."""
        with open(file, "rb") as f:
            toml_data = tomllib.load(f)

        tools = toml_data.get("tool", {})
        dbt_score_config = tools.get("dbt-score", {})
        rules_config = dbt_score_config.pop("rules", {})

        # Main configuration
        for option, value in dbt_score_config.items():
            if option in self._options:
                self.set_option(option, value)
            elif not isinstance(
                value, dict
            ):  # If value is a dictionary, it's another section
                logger.warning(
                    f"Option {option} in {self._main_section} not supported."
                )

        # Rule configuration
        self.rules_config = {
            name: RuleConfig.from_dict(config) for name, config in rules_config.items()
        }

    @staticmethod
    def get_config_file(directory: Path) -> Path | None:
        """Get the config file."""
        candidates = [directory]
        candidates.extend(directory.parents)
        for path in candidates:
            config_file = path / DEFAULT_CONFIG_FILE
            if config_file.exists():
                return config_file

    def load(self) -> None:
        """Load the config."""
        config_file = self.get_config_file(Path.cwd())
        if config_file:
            self._load_toml_file(str(config_file))
