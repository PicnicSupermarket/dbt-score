install:
	pre-commit install
	pdm install --group :all

lint:
	pdm run ruff check .
	pdm run ruff check --fix
	pdm run mypy .
	pdm run tox -e lint

format:
	pdm run ruff format .

test:
	pdm run tox -e py
	pdm run pytest
	pdm run coverage run -m pytest

docs:
	pdm run mkdocs build
	pdm run mkdocs serve

pre-commit:
	pre-commit run --all-files
