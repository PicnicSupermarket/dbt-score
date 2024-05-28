"""This module is responsible for loading configuration."""

import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from dbt_score.rule import RuleConfig

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = "pyproject.toml"


@dataclass
class MedalConfig:
    """Configuration for medals."""

    bronze_icon: str = "🥉"
    silver_icon: str = "🥈"
    gold_icon: str = "🥇"
    wip_icon: str = "🚧"
    bronze_threshold: float = 6.0
    silver_threshold: float = 8.0
    gold_threshold: float = 10.0

    @classmethod
    def load_from_dict(cls, medal_config: dict[str, Any]) -> "MedalConfig":
        """Create a MedalConfig from a dictionary."""
        options = {}
        for medal, medal_options in medal_config.items():
            if isinstance(medal_options, dict):
                for option, value in medal_options.items():
                    if not hasattr(cls, f"{medal}_{option}"):
                        raise AttributeError(
                            f"Unknown medal option: {option} for medal {medal}."
                        )
                    options[f"{medal}_{option}"] = value
            else:
                logger.warning(
                    f"Option {medal} in tool.dbt-score.medals not supported."
                )

        return cls(**options)

    def validate(self) -> None:
        """Validate the medal configuration."""
        if self.bronze_threshold >= self.silver_threshold:
            raise ValueError("bronze_threshold must be lower than silver_threshold")
        if self.silver_threshold >= self.gold_threshold:
            raise ValueError("silver_threshold must be lower than gold_threshold")


class Config:
    """Configuration for dbt-score."""

    _main_section: Final[str] = "tool.dbt-score"
    _main_options: Final[list[str]] = [
        "rule_namespaces",
        "disabled_rules",
    ]
    _rules_section: Final[str] = f"{_main_section}.rules"
    _medal_section: Final[str] = f"{_main_section}.medals"

    def __init__(self) -> None:
        """Initialize the Config object."""
        self.rule_namespaces: list[str] = ["dbt_score.rules", "dbt_score_rules"]
        self.disabled_rules: list[str] = []
        self.rules_config: dict[str, RuleConfig] = {}
        self.config_file: Path | None = None
        self.medal_config: MedalConfig = MedalConfig()

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
        medal_config = dbt_score_config.pop("medals", {})

        # Main configuration
        for option, value in dbt_score_config.items():
            if option in self._main_options:
                self.set_option(option, value)
            elif not isinstance(
                value, dict
            ):  # If value is a dictionary, it's another section
                logger.warning(
                    f"Option {option} in {self._main_section} not supported."
                )

        # Medal configuration
        if medal_config:
            self.medal_config = self.medal_config.load_from_dict(medal_config)
            self.medal_config.validate()

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

    def overload(self, values: dict[str, Any]) -> None:
        """Overload config with additional values."""
        for key, value in values.items():
            self.set_option(key, value)
