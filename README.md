# dbt-score

[![CI](https://github.com/PicnicSupermarket/dbt-score/actions/workflows/ci.yml/badge.svg)](https://github.com/PicnicSupermarket/dbt-score/actions)
[![PyPI version](https://img.shields.io/pypi/v/dbt-score.svg)](https://pypi.python.org/pypi/dbt-score/)
[![PyPI license](https://img.shields.io/pypi/l/dbt-score.svg)](https://pypi.python.org/pypi/dbt-score/)
[![Docs](https://img.shields.io/badge/Docs-mkdocs-blue)](https://dbt-score.picnic.tech/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dbt-score.svg)](https://pypi.org/project/dbt-score)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

**A comprehensive linter for dbt metadata that helps maintain high-quality data
models at scale.**

```shell
dbt-score lint
🥉 orders (score: 2.7)
  WARN (medium) dbt_score.rules.generic.columns_have_description: Columns lack a description: customer_id, customer_name.
  WARN (high) dbt_score.rules.generic.has_description: Model lacks a description.
  WARN (medium) dbt_score.rules.generic.has_owner: Model lacks an owner.
  WARN (medium) dbt_score.rules.generic.sql_has_reasonable_number_of_lines: SQL query too long: 238 lines (> 200).
  WARN (medium) dbt_score_rules.custom_rules.has_test: Model lacks a test.
```

## What is dbt-score?

`dbt-score` is a powerful linting tool designed to evaluate and score [dbt][dbt]
(Data Build Tool) models based on metadata quality. It helps data teams maintain
consistent standards across dbt projects by programmatically enforcing best
practices for documentation, testing, naming conventions, and more.

### Key Features

- 🔍 **Comprehensive Linting**: Evaluates dbt entities against configurable
  rules for documentation, tests, naming, and structure
- 📊 **Scoring System**: Provides numerical scores (0-10) for individual models
  and overall project health
- 🎯 **Flexible Configuration**: Customizable rules, severity levels, and
  scoring thresholds via `pyproject.toml`
- 🚀 **CI/CD Integration**: Fail builds when quality standards aren't met
- 📈 **Progress Tracking**: Visual badges and scoring to track data quality
  improvements over time
- 🔧 **Extensible**: Create custom rules tailored to organization-specific needs

## Quick Start

### Installation

```shell
pip install dbt-score
```

> **Note**: Install `dbt-score` in the same environment as `dbt-core`.

### Basic Usage

Run `dbt-score` from your dbt project root:

```bash
# Basic linting
dbt-score lint

# Also show passing tests
dbt-score lint --show all

# Lint specific models
dbt-score lint --select +my_model+

# Auto-generate manifest (via `dbt parse`) and lint
dbt-score lint --run-dbt-parse
```

### Example Output

```
dbt-score lint --show all
🥉 orders (score: 2.7)
  WARN (medium) dbt_score.rules.generic.columns_have_description: Columns lack a description: customer_id, customer_name.
  WARN (high) dbt_score.rules.generic.has_description: Model lacks a description.
  WARN (medium) dbt_score.rules.generic.has_owner: Model lacks an owner.
  WARN (medium) dbt_score.rules.generic.sql_has_reasonable_number_of_lines: SQL query too long: 238 lines (> 200).
  WARN (medium) dbt_score_rules.custom_rules.has_test: Model lacks a test.

🥇 customers (score: 10.0)
  OK    dbt_score.rules.generic.columns_have_description
  OK    dbt_score.rules.generic.has_description
  OK    dbt_score.rules.generic.has_owner
  OK    dbt_score.rules.generic.sql_has_reasonable_number_of_lines
  OK    dbt_score_rules.custom_rules.has_test

Project score: 6.3 🥈
```

## Configuration

Configure `dbt-score` via `pyproject.toml` in the dbt project root:

```toml
[tool.dbt-score]
# Fail CI if project score falls below threshold
fail_project_under = 7.5
fail_any_item_under = 8.0

# Disable specific rules
disabled_rules = ["dbt_score.rules.generic.columns_have_description"]

# Configure badges
[tool.dbt-score.badges]
first.threshold = 10.0
first.icon = "🥇"
second.threshold = 8.0
second.icon = "🥈"
third.threshold = 6.0
third.icon = "🥉"
wip.icon = "🏗️"

# Customize rule severity and parameters
[tool.dbt-score.rules."dbt_score.rules.generic.sql_has_reasonable_number_of_lines"]
severity = 1
max_lines = 300
```

## Why Use dbt-score?

As dbt projects grow to hundreds or thousands of models, maintaining consistent
metadata becomes increasingly challenging:

- **Inconsistent Documentation**: Some models are well-documented, others lack
  basic descriptions
- **Missing Tests**: Critical models without proper data quality tests
- **Naming Inconsistencies**: Models that don't follow established conventions
- **Technical Debt**: Long, complex SQL queries that are hard to maintain
- **Compliance Issues**: Missing ownership or governance metadata

`dbt-score` addresses these challenges by:

- **Automated Quality Checks**: Continuously evaluate dbt projects against best
  practices
- **Objective Scoring**: Get clear, numerical feedback on model quality
- **Team Alignment**: Establish shared standards across data teams
- **CI/CD Integration**: Prevent quality regressions in production

## Built-in Rules

`dbt-score` comes with a small set of rules covering needs applicable to most
dbt projects.

## Advanced Usage

### Custom Rules

Create organization-specific rules by writing simple Python functions:

```python
from dbt_score import Model, rule, RuleViolation

@rule
def model_has_business_owner(model: Model) -> RuleViolation:
    if model.meta.get("business_owner") is None:
        return RuleViolation("Model lacks a business owner.")
```

### CI/CD Integration

Add `dbt-score` to CI pipelines:

```yaml
- name: Run dbt-score
  run: |
    dbt-score lint --run-dbt-parse
```

or equivalent in your favourite CI platform. `dbt-score` exits with 0 or 1 to
signal success or failure, making integrations a breeze!

### Selective Linting

Use dbt's selection syntax to lint specific parts of projects:

```bash
# Lint only staging models
dbt-score lint --select staging.*

# Lint a model and its dependencies
dbt-score lint --select +my_important_model

# Lint recently changed models
dbt-score lint --select state:modified
```

## Documentation

For comprehensive documentation, including detailed rule descriptions,
configuration options, and advanced usage patterns, visit the [`dbt-score`
documentation website][dbt-score].

## Contributing

Contributions are welcome! This includes:

- Reporting bugs or requesting features
- Improving documentation
- Adding new rules or formatters
- Fixing issues

Check out the [contributing guide][contributors-guide] to get started. 🚀

## Requirements

- Python 3.10+
- dbt-core 1.5+

## License

This project is licensed under the MIT License - see the
[LICENSE.txt](LICENSE.txt) file for details.

---

[dbt]: https://github.com/dbt-labs/dbt-core
[dbt-score]: https://dbt-score.picnic.tech/
[contributors-guide]: https://dbt-score.picnic.tech/contributing/
