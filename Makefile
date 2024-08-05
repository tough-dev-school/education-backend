manage = poetry run python src/manage.py
SIMULTANEOUS_TEST_JOBS=4

compilemessages:
	$(manage) compilemessages

fmt:
	poetry run ruff format src
	poetry run ruff check src --fix --unsafe-fixes
	poetry run toml-sort pyproject.toml

lint:
	$(manage) makemigrations --check --no-input --dry-run
	poetry run ruff format --check src
	poetry run ruff check src
	poetry run mypy src
	poetry run toml-sort pyproject.toml --check
	poetry run pymarkdown scan README.md

messages: compilemessages
	$(manage) makemessages --locale ru

server: compilemessages
	$(manage) collectstatic --no-input

	$(manage) migrate
	$(manage) runserver

test:
	cd src && poetry run pytest -n ${SIMULTANEOUS_TEST_JOBS} --create-db --cov-report=xml --cov=. --junit-xml=junit-multithread.xml -m 'not single_thread'
	cd src && poetry run pytest --create-db --cov-report=xml --cov=. --cov-append --junit-xml=junit-singlethread.xml -m 'single_thread'
	cd src && poetry run pytest --dead-fixtures

worker:
	poetry run celery --app core --workdir src worker --events --purge
