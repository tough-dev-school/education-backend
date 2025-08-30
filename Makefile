manage = uv run python src/manage.py
SIMULTANEOUS_TEST_JOBS=4

compilemessages:
	$(manage) compilemessages

fmt:
	uv run ruff format src
	uv run ruff check src --fix --unsafe-fixes
	uv run toml-sort pyproject.toml

lint: lint-sources lint-dockerfile lint-yaml
	uv run toml-sort pyproject.toml --check
	uv run pymarkdown scan README.md

lint-sources:
	uv run ruff format --check src
	uv run ruff check src
	uv run mypy src
	$(manage) makemigrations --check --no-input --dry-run
	$(manage) check --fail-level WARNING
	$(manage) spectacular --api-version v1 --fail-on-warn > /dev/null

lint-dockerfile:
	@if command -v hadolint >/dev/null 2>&1; then \
		echo Running hadolint...; \
		hadolint Dockerfile; \
	else \
		echo "hadolint not found, skipping Dockerfile linting"; \
	fi

lint-yaml:
	@if command -v yamllint >/dev/null 2>&1; then \
		echo Running yamllint...; \
		yamllint .; \
	else \
		echo "yamllint not found, skipping YAML files linting"; \
	fi


messages: compilemessages
	$(manage) makemessages --locale ru

server: compilemessages
	$(manage) collectstatic --no-input

	$(manage) migrate
	$(manage) runserver

test:
	cd src && uv run pytest -n ${SIMULTANEOUS_TEST_JOBS} --create-db --cov-report=xml --cov=. --junit-xml=junit-multithread.xml -m 'not single_thread'
	cd src && uv run pytest --create-db --cov-report=xml --cov=. --cov-append --junit-xml=junit-singlethread.xml -m 'single_thread'
	cd src && uv run pytest --dead-fixtures

worker:
	uv run celery --app core --workdir src worker --events --purge
