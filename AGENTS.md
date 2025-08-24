# Django Backend Development Guide

## Development cycle
- Before writing any code, come up with a good plan, review the plan, and then ask the user for permission to execute the plan.

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
- Type checking: Use mypy annotations for all non-test code. Never use type annotations in tests until excplictly asked.
- Line length: 160 characters max
- Use absolute imports, no relative imports
- Format Python imports with standard library first, then third-party, then local
- Class/variable naming: Follow Django conventions with snake_case
- Error handling: Use typed exceptions with descriptive messages
- Documentation: Use docstrings for public methods, especially for complex functionality
- We do not need `__init__.py` in the management command or test folders
- Tests: Use pytest fixtures, keep tests atomic and isolated
- Tests: Use Model.update() for changing model properties in the test code. I.e. instead of `object.property = 'test' \n object.save()` use `object.update(property='test')`.


## Django Patterns
- Use Django ORM features (managers, querysets) over raw SQL
- Follow Django REST framework patterns for API endpoints
- Keep models thin, use services for business logic
- Use factory pattern for object creation in tests
- Use django.settings framework for constants: `from django.conf import settings` in the top module
- Never use exception checking in management commands
