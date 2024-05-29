"""This module is responsible for loading configuration."""

import logging
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

from dbt_score.rule import RuleConfig

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = "pyproject.toml"


@dataclass
class Medal:
    """Medal object."""

    icon: str
    threshold: float


@dataclass
class MedalConfig:
    """Configuration for medals."""

    bronze: Medal = field(default_factory=lambda: Medal("🥉", 6.0))
    silver: Medal = field(default_factory=lambda: Medal("🥈", 8.0))
    gold: Medal = field(default_factory=lambda: Medal("🥇", 10.0))
    wip: Medal = field(default_factory=lambda: Medal("🚧", 0.0))

    @classmethod
    def load_from_dict(cls, medal_config: dict[str, Any]) -> "MedalConfig":
        """Create a MedalConfig from a dictionary."""
        options = {}
        default_medal_config = cls()
        for medal, medal_options in medal_config.items():
            if medal not in default_medal_config.__dataclass_fields__:
                raise AttributeError(f"Unknown medal: {medal}.")
            if isinstance(medal_options, dict):
                medal_defaults = asdict(default_medal_config.__getattribute__(medal))
                medal_defaults.update(medal_options)
                options[medal] = Medal(**medal_defaults)
            else:
                raise AttributeError(
                    f"Invalid config for medal: {medal}, must be a dictionary."
                )

        return cls(**options)

    def validate(self) -> None:
        """Validate the medal configuration."""
        if self.bronze.threshold >= self.silver.threshold:
            raise ValueError("bronze threshold must be lower than silver threshold")
        if self.silver.threshold >= self.gold.threshold:
            raise ValueError("silver threshold must be lower than gold threshold")


class Config:
    """Configuration for dbt-score."""

    _main_section: Final[str] = "tool.dbt-score"
    _options: Final[list[str]] = [
        "rule_namespaces",
        "disabled_rules",
    ]
    _rules_section: Final[str] = "rules"
    _medals_section: Final[str] = "medals"

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
        rules_config = dbt_score_config.pop(self._rules_section, {})
        medal_config = dbt_score_config.pop(self._medals_section, {})

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
