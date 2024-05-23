# Getting started

`dbt-score` is a Python library that is easy to install and use. The minimum
required version of Python is `3.11`.

There are two dependencies:

- `dbt-core`: To parse a dbt project.
- `click`: To run the CLI.

## Installation

The easiest way to install `dbt-score` is with `pip`:

```shell
pip install dbt-score
```

## Usage

`dbt-score` uses the output of `dbt parse` (`manifest.json`) as input.
Therefore, it is recommended to run `dbt-score` from the root of your dbt
project. By default, it will look for `manifest.json` in dbt's `target`
directory.

`dbt-score` can be executed from the command line:

```shell
dbt-score lint
```

To use a different manifest file, use the `--manifest` option:

```shell
dbt-score lint --manifest path/to/manifest.json
```

It's also possible to automatically run `dbt parse`, to generate the
`manifest.json` file:

```shell
dbt-score lint --run-dbt-parse
```
