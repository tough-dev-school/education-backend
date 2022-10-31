# Backend for [education.borshev.com](http://education.borshev.com/)

![CI](https://github.com/tough-dev-school/education-backend/actions/workflows/ci.yml/badge.svg) ![](https://heroku-badge.herokuapp.com/?app=education-backend&svg=1) [![Maintainability](https://api.codeclimate.com/v1/badges/fe9fb0b64052a426f355/maintainability)](https://codeclimate.com/github/f213/education-backend/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/fe9fb0b64052a426f355/test_coverage)](https://codeclimate.com/github/f213/education-backend/test_coverage) 

Django-based production project, integrated with Tinkoff, zoom.us, Dashamail, Postmark, S3 and telegram. Frontend is built on vue.js in the [separate repo](http://github.com/f213/education-frontend).

## Configuration
Configuration is stored in `src/app/.env`, for examples see `src/app/.env.ci`


## Installing on a local machine
This project requires python 3.10. Python virtual environment should be installed and activated.\
Deps are managed by [pip-tools](https://github.com/jazzband/pip-tools) with requirements stored in [pyproject.toml](https://github.com/jazzband/pip-tools#requirements-from-pyprojecttoml).

Install requirements:

```bash
pip install --upgrade pip pip-tools
make
```

Configure postgres and redis. It's convenient to use docker and docker-compose:

```bash
docker-compose up -d
```

If you don't have access to de-anonymized db image use `postgres:13.6-alpine` in `docker-compose.yml` instead:
```yaml
postgres:
    image: postgres:13.6-alpine
    ...
```

Run the server:

```bash
cd src && cp app/.env.ci app/.env  # default environment variables
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```

Testing:
```bash
# run lint
make -C .. lint

# run unit tests
make -C .. test
```

## Backend Code requirements

### Style

* Obey [django's style guide](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style).
* Configure your IDE to use [flake8](https://pypi.python.org/pypi/flake8) for checking your python code. For running flake8 manualy, do `cd src && flake8`
* Prefer English over your native language in comments and commit messages.
* Commit messages should contain the unique id of issue they are linked to (refs #100500)
* Every model and a model method should have a docstring.

### Code organisation

* KISS and DRY.
* Obey [django best practices](http://django-best-practices.readthedocs.io/en/latest/index.html)
* If you want to implement some business logic — make a service for that. Service examples: [UserCreator](https://github.com/tough-dev-school/education-backend/blob/master/src/users/services/user_creator.py#L22), [OrderCreator](https://github.com/tough-dev-school/education-backend/blob/master/src/orders/services/order_creator.py#L11)
* **No logic is allowed within the views or templates**. Only services and models.
* Use PEP-484 [type hints](https://www.python.org/dev/peps/pep-0484/) when possible.
* Prefer [Manager](https://docs.djangoproject.com/en/1.10/topics/db/managers/) methods over static methods.
* Do not use [signals](https://docs.djangoproject.com/en/1.10/topics/signals/) for business logic. Signals are good only for notification purposes.
* No l10n is allowed in python code, use [django translation](https://docs.djangoproject.com/en/1.10/topics/i18n/translation/).
