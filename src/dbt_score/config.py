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

    @classmethod
    def load_from_dict(cls, badge_config: dict[str, Any]) -> "BadgeConfig":
        """Create a BadgeConfig from a dictionary."""
        options: dict[str, Any] = {}
        default_badge_config = cls()
        for badge, badge_options in badge_config.items():
            if badge not in default_badge_config.__dataclass_fields__:
                raise AttributeError(f"Unknown badge: {badge}.")
            if isinstance(badge_options, dict):
                badge_defaults = asdict(default_badge_config.__getattribute__(badge))
                badge_defaults.update(badge_options)
                options[badge] = Badge(**badge_defaults)

                if badge == "wip" and badge_options.get("threshold"):
                    raise AttributeError(
                        "wip badge cannot have a threshold configuration."
                    )
            else:
                raise AttributeError(
                    f"Invalid config for badge: {badge}, must be a dictionary."
                )

        config = cls(**options)
        config.validate()

        return config

    def validate(self) -> None:
        """Validate the badge configuration."""
        if self.third.threshold >= self.second.threshold:
            raise ValueError("third threshold must be lower than second threshold")
        if self.second.threshold >= self.first.threshold:
            raise ValueError("second threshold must be lower than first threshold")
        if self.first.threshold > 10.0:  # noqa: PLR2004 [magic-value-comparison]
            raise ValueError("first threshold must 10.0 or lower")
        if self.third.threshold < 0.0:
            raise ValueError("third threshold must be 0.0 or higher")


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
        if badge_config:
            self.badge_config = self.badge_config.load_from_dict(badge_config)

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
