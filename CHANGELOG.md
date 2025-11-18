# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.15.0] - 2025-11-19

- Round score of individual entities when showing summary.
- Support linting dbt macros as a new evaluable entity type.

## [0.14.1] - 2025-10-09

- Migrate to `uv` project manager.

## [0.14.0] - 2025-08-08

- Display the parse error message when `dbt parse` fails.
- **Breaking**: JSON-formatted output is using `unique_id` as key instead of
  `name`, to avoid duplicates (e.g if exposure and model have the same name).

## [0.13.1] - 2025-07-29

- Fix filters being applied to wrong evaluables (#124)

## [0.13.0] - 2025-07-07

- Support linting of exposures (#112)
- Fix retrieval of data_tests when using quoted columns in BigQuery (#122)

## [0.12.0] - 2025-05-06

- Add support for linting and scoring dbt seeds (#110)
- Add `children` to models, snapshots, and sources. (#113)
- Add `parents` to models and snapshots, allowing access to parent nodes. (#109)

## [0.11.0] - 2025-04-04

- Improve documentation on rule filters. (#93)
- Add `group` to model definition. (#99)
- Add rule: prevent use of is_incremental() in non-incremental models. (#103)
- Support linting of snapshots. (#96)

## [0.10.0] - 2025-01-27

- Add debug mode to help writing new rules. (#91)
- Fix tests without metadata. (#88)
- Add new rule to enforce presence of uniqueness test. (#90)
- Add new rule to enforce single-column PK to be defined at column level. (#90)
- Add new rule to enforce 1 column uniqueness test to be defined at column
  level. (#90)
- Add `constraints` to the model schema. (#90)

## [0.9.0] - 2024-12-19

- Documenting support for python 3.13. (#86)
- Only show failing rules per default in `HumanReadableFormatter`. Also added
  `--show` parameter in the CLI to change this behavior. (#77)
- Ignore imported rules and filters when building the rule registry. (#87)

## [0.8.0] - 2024-11-12

- Support linting of sources.
- **Breaking**: Renamed modules: `dbt_score.model_filter` becomes
  `dbt_score.rule_filter`
- **Breaking**: Renamed filter class and decorator: `@model_filter` becomes
  `@rule_filter` and `ModelFilter` becomes `RuleFilter`.
- **Breaking**: Config option `model_filter_names` becomes `rule_filter_names`.
- **Breaking**: CLI flag naming fixes: `--fail_any_model_under` becomes
  `--fail-any-item-under` and `--fail_project_under` becomes
  `--fail-project-under`.

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
