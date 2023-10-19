poetry = cd src && poetry run
manage = $(poetry) python manage.py

server:
	$(manage) migrate
	$(manage) runserver

worker:
	$(poetry) celery -A app worker -E --purge

fmt:
	$(poetry) autoflake --in-place --remove-all-unused-imports --recursive .
	$(poetry) isort .
	$(poetry) black .

lint:
	$(manage) makemigrations --check --no-input --dry-run
	$(poetry) flake8 .
	$(poetry) mypy

test:
	poetry run pytest -n 4 --ff -x --create-db --cov-report=xml --cov=. -m 'not single_thread'
	poetry run pytest --ff -x --cov-report=xml --cov=. --cov-append -m 'single_thread'
	poetry run pytest --dead-fixtures
