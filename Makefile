manage = poetry run python src/manage.py
SIMULTANEOUS_TEST_JOBS=4

compilemessages:
	$(manage) compilemessages

flint:
	poetry run ruff src tests --fix
	poetry run black src tests
	poetry run toml-sort pyproject.toml

lint:
	$(manage) makemigrations --check --no-input --dry-run
	poetry run ruff src tests
	poetry run flake8 src tests
	poetry run mypy src tests
	poetry run pymarkdown scan README.md

messages: compilemessages
	$(manage) makemessages --locale ru

server: compilemessages
	$(manage) collectstatic --no-input

	$(manage) migrate
	$(manage) runserver

test:
	poetry run pytest -n ${SIMULTANEOUS_TEST_JOBS} --create-db --cov-report=xml --cov=. --junit-xml=junit-multithread.xml -m 'not single_thread'
	poetry run pytest --cov-report=xml --cov=. --cov-append --junit-xml=junit-singlethread.xml -m 'single_thread'
	poetry run pytest --dead-fixtures

worker:
	poetry run celery --app core --workdir src worker --events --purge
