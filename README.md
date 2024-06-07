# dbt-score

[![CI](https://github.com/PicnicSupermarket/dbt-score/actions/workflows/ci.yml/badge.svg)](https://github.com/PicnicSupermarket/dbt-score/actions)
[![PyPI version](https://img.shields.io/pypi/v/dbt-score.svg)](https://pypi.python.org/pypi/dbt-score/)
[![PyPI license](https://img.shields.io/pypi/l/dbt-score.svg)](https://pypi.python.org/pypi/dbt-score/)
[![Docs](https://img.shields.io/badge/Docs-mkdocs-blue)](https://dbt-score.picnic.tech/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dbt-score.svg)](https://pypi.org/project/dbt-score)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

## What is `dbt-score`?

`dbt-score` is a linter for dbt model metadata.

[dbt](https://getdbt.com/) (Data Build Tool) is a great framework for creating,
building, organizing, testing and documenting _data models_, i.e. data sets
living in a database or a data warehouse. Through a declarative approach, it
allows data practitioners to build data with a methodology inspired by software
development practices.

This leads to data models being bundled with a lot of metadata, such as
documentation, data tests, access control information, column types and
constraints, 3rd party integrations... Not to mention any other metadata that
organizations need, fully supported through the `meta` parameter.

At scale, with hundreds or thousands of data models, all this metadata can
become confusing, disparate, and inconsistent. It's hard to enforce good
practices and maintain them in continuous integration systems. This is where
`dbt-score` plays its role: by allowing data teams to programmatically define
and enforce metadata rules, in an easy and scalable manner.

## Documentation

Everything you need (and more) can be found in
[`dbt-score` documentation website](https://dbt-score.picnic.tech/).

## Contributing

Would you like to contribute to `dbt-score`? That's great news! Please follow
[the guide on the documentation website](https://dbt-score.picnic.tech/contributors_guide).
🚀
