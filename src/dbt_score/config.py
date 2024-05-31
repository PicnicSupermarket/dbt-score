"""This module is responsible for loading configuration."""

import logging
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Final

from dbt_score.rule import RuleConfig

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = "pyproject.toml"


@dataclass
class Badge:
    """Badge object."""

    icon: str
    threshold: float


@dataclass
class BadgeConfig:
    """Configuration for badges."""

    third: Badge = field(default_factory=lambda: Badge("🥉", 6.0))
    second: Badge = field(default_factory=lambda: Badge("🥈", 8.0))
    first: Badge = field(default_factory=lambda: Badge("🥇", 10.0))
    wip: Badge = field(default_factory=lambda: Badge("🚧", 0.0))

    def validate(self) -> None:
        """Validate badges config."""
        try:
            assert (
                self.first.threshold > self.second.threshold > self.third.threshold
            ), "Bad threshold values"
            assert self.third.threshold > 0, "Threshold must be greater than zero"
            assert self.wip.threshold == 0, "WIP threshold must be equal to 0"
        except AssertionError as e:
            raise ValueError(f"Invalid badges config. {e!s}") from e


class Config:
    """Configuration for dbt-score."""

    _main_section: Final[str] = "tool.dbt-score"
    _options: Final[list[str]] = [
        "rule_namespaces",
        "disabled_rules",
    ]
    _rules_section: Final[str] = "rules"
    _badges_section: Final[str] = "badges"

    def __init__(self) -> None:
        """Initialize the Config object."""
        self.rule_namespaces: list[str] = ["dbt_score.rules", "dbt_score_rules"]
        self.disabled_rules: list[str] = []
        self.rules_config: dict[str, RuleConfig] = {}
        self.config_file: Path | None = None
        self.badge_config: BadgeConfig = BadgeConfig()

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
        badge_config = dbt_score_config.pop(self._badges_section, {})

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

        # Badge configuration
        for name, config in badge_config.items():
            try:
                badge = getattr(self.badge_config, name)
                setattr(self.badge_config, name, replace(badge, **config))
            except AttributeError as e:
                options = list(BadgeConfig.__annotations__.keys())
                raise ValueError(f"Config only accepts {options}") from e
            except TypeError as e:
                options = list(Badge.__annotations__.keys())
                raise ValueError(f"Badge config only accepts {options}") from e

        self.badge_config.validate()

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
