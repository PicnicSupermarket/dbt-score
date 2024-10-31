# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- **Breaking**: Support linting of sources.
- **Breaking**: `--fail_any_model_under` becomes `--fail-any-item-under` and
  `--fail_project_under` becomes `--fail-project-under`.
- **Breaking**: `model_filter_names` becomes `rule_filter_names`.

## [0.7.1] - 2024-11-01

- Fix mkdocs.

## [0.7.0] - 2024-11-01

- **Breaking**: The rule `public_model_has_example_sql` has been renamed
  `has_example_sql` and applies by default to all models.
- **Breaking**: Remove `dbt-core` from dependencies. Since it is not mandatory
  for `dbt-score` to execute `dbt`, remove the dependency.
- **Breaking**: Stop using `MultiOption` selection type.

## [0.6.0] - 2024-08-23

- **Breaking**: Improve error handling in CLI. Log messages are written in
  stderr, and exit code is 2 in case of anything going wrong. (#73)
- Auto-round scores down to align scores and medals. (#74)

## [0.5.0] - 2024-08-15

- Add model filters to let models be ignored by certain rules.

## [0.4.0] - 2024-08-08

- Add null check before calling `project_evaluated` in the `evaluate` method to
  prevent errors when no models are found. (#64)
- Add JSON formatter for machine-readable output. (#68)

## [0.3.0] - 2024-06-20

### Added

- Add `project_fail_under` configuration.
- Add `fail_any_model_under` configuration.
- **Breaking:** default values of `5.0` for `project_fail_under` and
  `fail_any_model_under` will cause command to exit return code 1.

## [0.2.1] - 2024-06-17

### Added

- Lint the current dbt project only, not including the imported models.

## [0.2.0] - 2024-06-14

### Added

- Support Python 3.10.

## [0.1.3] - 2024-06-11

### Added

- Inject current working directory into python path by default.

## [0.1.2] - 2024-06-07

### Added

- Create contributors guide for the documentation website.
- Add Github icon and link to documentation website.

## [0.1.1] - 2024-06-03

### Added

- CLI based on Click.
- Ability to parse dbt's `manifest.json` into internal structures.
- Rule registry and rule discovery.
- Rule API, decorator-based or class-based.
- Linting and scoring functionality for dbt models.
- Configuration through `pyproject.toml`.
- Default rules in `dbt_score.rules.generic`.
- Badges for project and model evaluation.
