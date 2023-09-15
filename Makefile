poetry-src = cd src && poetry run
manage = $(poetry-src) python manage.py

server:
	$(manage) migrate
	$(manage) runserver

worker:
	$(poetry-src) celery -A app worker -E --purge

fmt:
	$(poetry-src) autoflake --in-place --remove-all-unused-imports --recursive .
	$(poetry-src) isort .
	$(poetry-src) black .

lint:
	$(manage) makemigrations --check --no-input --dry-run
	$(poetry-src) flake8 .
	$(poetry-src) mypy

test:
	$(poetry-src) pytest -n 4 --ff -x --create-db --cov-report=xml --cov=. -m 'not single_thread'
	$(poetry-src) pytest --ff -x --cov-report=xml --cov=. --cov-append -m 'single_thread'
	$(poetry-src) pytest --dead-fixtures
