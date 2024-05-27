# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CLI based on Click.
- Ability to parse dbt's `manifest.json` into internal structures.
- Rule registry and rule discovery.
- Rule API, decorator-based or class-based.
- Linting and scoring functionality for dbt models.
- Configuration through `pyproject.toml`.
- Default rules in `dbt_score.rules.generic`.
