"""Human readable formatter."""

from typing import Any

from dbt_score.evaluation import ModelResultsType
from dbt_score.formatters import Formatter
from dbt_score.models import Model
from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score


class HumanReadableFormatter(Formatter):
    """Formatter for human-readable messages in the terminal."""

    indent = "    "
    label_ok = "\033[1;32mOK  \033[0m"
    label_warning = "\033[1;33mWARN\033[0m"
    label_error = "\033[1;31mERR \033[0m"

    def __init__(self, *args: Any, **kwargs: Any):
        """Instantiate formatter."""
        super().__init__(*args, **kwargs)
        self._failed_models: list[tuple[Model, Score]] = []

    @staticmethod
    def bold(text: str) -> str:
        """Return text in bold."""
        return f"\033[1m{text}\033[0m"

    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: Score
    ) -> None:
        """Callback when a model has been evaluated."""
        if score.value < self._config.fail_any_model_under:
            self._failed_models.append((model, score))
        print(f"{score.badge} {self.bold(model.name)} (score: {score.rounded_value!s})")
        for rule, result in results.items():
            if result is None:
                print(f"{self.indent}{self.label_ok} {rule.source()}")
            elif isinstance(result, RuleViolation):
                print(
                    f"{self.indent}{self.label_warning} "
                    f"({rule.severity.name.lower()}) {rule.source()}: {result.message}"
                )
            else:
                print(f"{self.indent}{self.label_error} {rule.source()}: {result!s}")
        print()

    def project_evaluated(self, score: Score) -> None:
        """Callback when a project has been evaluated."""
        print(f"Project score: {self.bold(str(score.rounded_value))} {score.badge}")

        if len(self._failed_models) > 0:
            print()
            print(
                f"Error: model score too low, fail_any_model_under = "
                f"{self._config.fail_any_model_under}"
            )
            for model, model_score in self._failed_models:
                print(f"Model {model.name} scored {model_score.value}")

        elif score.value < self._config.fail_project_under:
            print()
            print(
                f"Error: project score too low, fail_project_under = "
                f"{self._config.fail_project_under}"
            )
