manage = poetry run python src/manage.py

server:
	$(manage) migrate
	$(manage) runserver

worker:
	poetry run celery --app core --workdir src worker --events --purge

fmt:
	poetry run autoflake --in-place --remove-all-unused-imports --recursive src
	poetry run isort src
	poetry run black src

lint:
	$(manage) makemigrations --check --no-input --dry-run
	poetry run flake8 src
	poetry run mypy src

test:
	poetry run pytest -n 4 --ff -x --create-db --cov-report=xml --cov=. -m 'not single_thread'
	poetry run pytest --ff -x --cov-report=xml --cov=. --cov-append -m 'single_thread'
	poetry run pytest --dead-fixtures
