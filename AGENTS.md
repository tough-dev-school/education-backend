# Django Backend Development Guide

## Development cycle
- Ignore all typing errors if the code is a valid python
- Do not generate or run any tests until asked explicitly
- Prefer Django ORM features (managers, querysets) over raw SQL
- Keep models thin, use services for business logic
- Use factory pattern for object creation in tests
- Never check exceptions in the management commands


## Build/Test Commands
- Use uv for package management and running commands
- `make fmt` - Format the code using ruff
- `make lint` - Run all linters (ignore mypy errors)
- Run a single test: `cd src && uv run python -m pytest path/to/test_file.py::test_function -v`
- Run tests matching pattern: `cd src && uv run python -m pytest -k "pattern" -v`
- Run server: `make server`
- Run worker: `make worker`
- Run django manage command: `cd src && uv run python manage.py`


## Code Style
- Line length: 160 characters max
- Type checking: Use mypy annotations for all non-test code. Never use type annotations in tests
- Use absolute imports, no relative imports
- Class/variable naming: Follow Django conventions with snake_case
- Never create `__init__.py`
- Tests: Use pytest fixtures, keep tests atomic and isolated
- Tests: Use Model.update() for changing model properties in the test code. I.e. instead of `object.property = 'test' \n object.save()` use `object.update(property='test')`.
