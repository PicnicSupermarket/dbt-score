"""Human readable formatter."""


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

    @staticmethod
    def bold(text: str) -> str:
        """Return text in bold."""
        return f"\033[1m{text}\033[0m"

    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: Score
    ) -> None:
        """Callback when a model has been evaluated."""
        print(
            f"{score.badge} {self.bold(model.name)} (score: {round(score.value, 1)!s})"
        )
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
        print(f"Project score: {self.bold(str(round(score.value, 1)))} {score.badge}")
