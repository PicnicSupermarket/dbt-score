"""JSON formatter.

Shape of the JSON output:

```json
{
    "models": {
        "model_foo": {
            "score": 5.0,
            "badge": "🥈",
            "pass": true,
            "results": {
                "rule1": {
                    "result": "OK",
                    "severity": null
                    "message": null
                },
                "rule2": {
                    "result": "WARN",
                    "severity": "medium",
                    "message": "Model lacks a description."
                }
            ]
        },
        "model_bar": {
            "score": 0.0,
            "badge": "🥉",
            "pass": false,
            "results": {
                "rule1": {
                    "result": "ERR",
                    "message": "Exception message"
                }
            }
        }
    },
    "project": {
        "score": 2.5,
        "badge": "🥉",
        "pass": false
    }
}
```
"""


import json
from typing import Any

from dbt_score.evaluation import ModelResultsType
from dbt_score.formatters import Formatter
from dbt_score.models import Model
from dbt_score.rule import RuleViolation
from dbt_score.scoring import Score


class JSONFormatter(Formatter):
    """Formatter for JSON output."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Instantiate formatter."""
        super().__init__(*args, **kwargs)
        self._model_results: dict[str, dict[str, Any]] = {}
        self._project_results: dict[str, Any]

    def model_evaluated(
        self, model: Model, results: ModelResultsType, score: Score
    ) -> None:
        """Callback when a model has been evaluated."""
        self._model_results[model.name] = {
            "score": score.value,
            "badge": score.badge,
            "pass": score.value >= self._config.fail_any_model_under,
            "results": {},
        }
        for rule, result in results.items():
            severity = rule.severity.name.lower()
            if result is None:
                self._model_results[model.name]["results"][rule.source()] = {
                    "result": "OK",
                    "severity": severity,
                    "message": None,
                }
            elif isinstance(result, RuleViolation):
                self._model_results[model.name]["results"][rule.source()] = {
                    "result": "WARN",
                    "severity": severity,
                    "message": result.message,
                }
            else:
                self._model_results[model.name]["results"][rule.source()] = {
                    "result": "ERR",
                    "severity": severity,
                    "message": str(result),
                }

    def project_evaluated(self, score: Score) -> None:
        """Callback when a project has been evaluated."""
        self._project_results = {
            "score": score.value,
            "badge": score.badge,
            "pass": score.value >= self._config.fail_project_under,
        }
        document = {
            "models": self._model_results,
            "project": self._project_results,
        }
        print(json.dumps(document, indent=2, ensure_ascii=False))
