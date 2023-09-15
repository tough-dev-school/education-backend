manage = cd src && poetry run python manage.py

server:
	$(manage) migrate
	$(manage) runserver

worker:
	cd src && poetry run celery -A app worker -E --purge

fmt:
	cd src && poetry run autoflake --in-place --remove-all-unused-imports --recursive .
	cd src && poetry run isort .
	cd src && poetry run black .

lint:
	$(manage) makemigrations --check --no-input --dry-run
	poetry run flake8 src
	cd src && poetry run mypy

test:
	cd src && poetry run pytest -n 4 --ff -x --create-db --cov-report=xml --cov=. -m 'not single_thread'
	cd src && poetry run pytest --ff -x --cov-report=xml --cov=. --cov-append -m 'single_thread'
	cd src && poetry run pytest --dead-fixtures
