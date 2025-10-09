# Contributor's guide

`dbt-score` is free software, your contributions are welcome! 🚀

## Reporting bugs

If you encountered a bug, check the
[issue tracker on Github](https://github.com/PicnicSupermarket/dbt-score/issues)
to see if it is already known. If not, feel free to
[open a new issue](https://github.com/PicnicSupermarket/dbt-score/issues/new).
Share all relevant details, especially how to reproduce the problem.

We'd love to hear from you and help make `dbt-score` as stable as we can.

## Developing new features

### Adding rules

The linting rules bundled with `dbt-score` aim to be as generic as possible, and
apply to a large majority of dbt projects.

This is why they are not very opinionated: for example, we believe documenting
data models is important, and hope it's not a controversial opinion ;) Of
course, it's always possible to disable any rule.

If you think a new rule should be created in `dbt-score`, feel free to
[open an issue](https://github.com/PicnicSupermarket/dbt-score/issues/new) to
discuss it first - this might save you some work in case maintainers don't see a
fit.

If your rule idea is not generic and applies to your own project and logic,
`dbt-score` has been designed to fully [support custom rules](create_rules.md).
Create as many as you need for your purposes!

### Fixing bugs

We love bug squashing! You can open a pull request to fix any bug you encounter
in `dbt-score`. If the changes are large enough, refer to the next section
first - discussing a solution in a Github issue is always a good idea to avoid
unnecessary work and orchestrate efforts.

### Adding or changing core features

Before implementing or changing a new feature, we kindly ask you to
[open a Github issue](https://github.com/PicnicSupermarket/dbt-score/issues/new/)
to get the maintainers' opinion on that feature. It might have been already
considered, discussed, or already in the works.

We aim to maintain a high code coverage in `dbt-score`'s unit tests, so new
features should be properly tested for happy and unhappy paths.

If the feature has direct impact on users, it should also be reflected in the
documentation website.

## Development environment

### Prerequisites

You'll need the following:

- Any Python version starting from 3.10
- [pre-commit](https://pre-commit.com/) (recommended)
- [uv](https://docs.astral.sh/uv/)

After cloning the repository with git, configure your development environment by
running these commands from the project's root:

```shell
pre-commit install
uv sync --all-groups
```

The uv command will install all project's dependency groups, including all the
dependencies needed for development purposes.

### Lint

`dbt-score` uses:

- [ruff](https://docs.astral.sh/ruff/) for fast linting and formatting.
- [mypy](https://mypy.readthedocs.io/en/stable/) for type checking.
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks).
- [prettier-hooks](https://github.com/pre-commit/mirrors-prettier).

Cheatsheet:

```shell
uv run ruff check .
uv run ruff check --fix
uv run mypy .
uv run tox -e lint
```

### Test

`dbt-score` uses:

- [pytest](https://docs.pytest.org/) as a main test framework.
- [coverage](https://coverage.readthedocs.io/en/latest/index.html) for test
  coverage.
- [tox](https://tox.wiki/en/latest/) for testing against multiple Python
  versions.

Cheatsheet:

```shell
uv run tox -e py
uv run pytest
uv run coverage run -m pytest
```

### Docs

`dbt-score` uses:

- [mkdocs](https://www.mkdocs.org/) for docs generation.
- [mkdocstrings](https://mkdocstrings.github.io/) for automatic docs from
  sources.

Cheatsheet:

```shell
uv run mkdocs build
uv run mkdocs serve
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
