# dbt-score

Linter for dbt model metadata.

## Development

### Prerequisites

You'll need the following prerequisites:

- Any Python version starting from 3.10
- [pre-commit](https://pre-commit.com/)
- [PDM](https://pdm-project.org/2.12/)

Configure development environment running these commands from the project's root:

```shell
pre-commit install
pdm install --group :all
```

The pdm command will install all project's dependency groups, including all the dependencies needed for development
purposes.

### Lint

`dbt_score` uses:

- [ruff](https://docs.astral.sh/ruff/) for fast linting and formatting.
- [mypy](https://mypy.readthedocs.io/en/stable/) for type checking.
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks).
- [prettier-hooks](https://github.com/pre-commit/mirrors-prettier).

Cheatsheet:

```shell
pdm run ruff check .
pdm run ruff check --fix
pdm run mypy .
pdm run tox -e lint
```

### Test

`dbt_score` uses:

- [pytest](https://docs.pytest.org/) as a main test framework.
- [coverage](https://coverage.readthedocs.io/en/latest/index.html) for test coverage.
- [tox](https://tox.wiki/en/latest/) for testing against multiple Python versions.

Cheatsheet:

```shell
pdm run tox -e py
pdm run pytest
pdm run coverage run -m pytest
```

### Docs

`dbt_score` uses:

- [mkdocs](https://www.mkdocs.org/) for docs generation.
- [mkdocstrings](https://mkdocstrings.github.io/) for automatic docs from sources.

Cheatsheet:

```shell
pdm run mkdocs build
pdm run mkdocs serve
```

### Pre-commit

Cheatsheet:

Execute hooks manually:

```shell
pre-commit run --all-files
```

Create a commit bypassing hooks:

```shell
git commit --no-verify
```
