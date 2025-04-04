# Django Backend Development Guide

## Build/Test Commands
- Use poetry for package management and running commands
- `make fmt` - Format the code using ruff
- `make lint` - Run all linters (django migrations check, ruff, mypy, etc.)
- `make test` - Run all tests with coverage
- Run a single test: `cd src && poetry run python -m pytest path/to/test_file.py::test_function -v`
- Run tests matching pattern: `cd src && poetry run python -m pytest -k "pattern" -v`
- Run server: `make server`
- Run worker: `make worker`
- Run django manage command: `cd src && poetry run python manage.py`
- Do not run tests or make commits until i ask explicitly


## Code Style
- Type checking: Use mypy annotations for all non-test code
- Line length: 160 characters max
- Use absolute imports, no relative imports
- Format Python imports with standard library first, then third-party, then local
- Class/variable naming: Follow Django conventions with snake_case
- Error handling: Use typed exceptions with descriptive messages
- Tests: Use pytest fixtures, keep tests atomic and isolated
- Documentation: Use docstrings for public methods, especially for complex functionality
- We do not need `__init__.py` in the management command or test folders


## Django Patterns
- Use Django ORM features (managers, querysets) over raw SQL
- Follow Django REST framework patterns for API endpoints
- Keep models thin, use services for business logic
- Use factory pattern for object creation in tests
- Never use exception checking in management commands
