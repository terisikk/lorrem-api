.PHONY: install
install:
	pipx install poetry==1.4.0
	poetry install && poetry build

.PHONY: lint
lint:
	poetry run bandit -c pyproject.toml -q -r .
	poetry run ruff check .
	poetry run ruff format --check .

.PHONY: format
format:
	poetry run ruff format .

# Lcov report included for vscode coverage
.PHONY: test
test:
	poetry run coverage run
	poetry run coverage report

.PHONY: coverage-lcov
coverage-lcov:
	poetry run coverage lcov

.PHONY: serve
serve:
	poetry run flask --app app run --host 0.0.0.0
