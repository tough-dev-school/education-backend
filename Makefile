install-dev-deps: dev-deps
	pip-sync requirements.txt dev-requirements.txt

install-deps: deps
	pip-sync requirements.txt

deps:
	pip install --upgrade pip pip-tools
	pip-compile --output-file requirements.txt --resolver=backtracking pyproject.toml

dev-deps: deps
	pip-compile --extra=dev --output-file dev-requirements.txt --resolver=backtracking pyproject.toml

server:
	cd src && ./manage.py migrate && ./manage.py runserver

worker:
	cd src && celery -A app worker -E --purge

fmt:
	cd src && autoflake --in-place --remove-all-unused-imports --recursive .
	cd src && isort .
	cd src && black .

lint:
	cd src && ./manage.py makemigrations --check --no-input --dry-run
	flake8 src
	cd src && mypy

test:
	cd src && pytest -n 4 --ff -x --create-db --cov-report=xml --cov=. -m 'not single_thread'
	cd src && pytest --ff -x --cov-report=xml --cov=. --cov-append -m 'single_thread'
	cd src && pytest --dead-fixtures
