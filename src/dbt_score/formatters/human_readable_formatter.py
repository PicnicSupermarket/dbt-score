"""Human readable formatter."""

from typing import Any

from dbt_score.evaluation import EvaluableResultsType
from dbt_score.formatters import Formatter
from dbt_score.models import Model, Evaluable
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
        self._failed_evaluables: list[tuple[Evaluable, Score]] = []

    @staticmethod
    def bold(text: str) -> str:
        """Return text in bold."""
        return f"\033[1m{text}\033[0m"

    def evaluable_evaluated(
        self, evaluable: Evaluable, results: EvaluableResultsType, score: Score
    ) -> None:
        """Callback when an evaluable item has been evaluated."""
        if score.value < self._config.fail_any_evaluable_under:
            self._failed_evaluables.append((evaluable, score))
        print(f"{score.badge} {self.bold(evaluable.name)} (score: {score.rounded_value!s})")
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

        if len(self._failed_evaluables) > 0:
            print()
            print(
                f"Error: evaluable score too low, fail_any_evaluable_under = "
                f"{self._config.fail_any_evaluable_under}"
            )
            for evaluable, evaluable_score in self._failed_evaluables:
                print(f"Model {evaluable.name} scored {evaluable_score.value}")

        elif score.value < self._config.fail_project_under:
            print()
            print(
                f"Error: project score too low, fail_project_under = "
                f"{self._config.fail_project_under}"
            )
