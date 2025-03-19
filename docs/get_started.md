# Get started

`dbt-score` is a Python library that is easy to install and use. The minimum
required version of Python is `3.10`.

## Installation

Installation of `dbt-score` is simple:

```shell
pip install dbt-score
```

In order to run `dbt-score` with all its features, be sure to install
`dbt-score` in the same environment as `dbt-core`.

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

To lint only a selection of dbt entities, the argument `--select` can be used.
It accepts any
[dbt node selection syntax](https://docs.getdbt.com/reference/node-selection/syntax):

```shell
dbt-score lint --select +my_model+
```

To get more information on how to run `dbt-score`, `--help` can be used:

```shell
dbt-score --help
```

```shell
dbt-score lint --help
```
