# pmdaily-backend

[![CircleCI](https://circleci.com/gh/f213/pmdaily-backend.svg?style=svg&circle-token=7928e0697de3b475905f58e96311c3df3e55eccc)](https://circleci.com/gh/f213/pmdaily-backend)

Это бекенд, который используется для продажи курсов на сайте pmdaily.ru.

## Configuration
Configuration is stored in `src/app/.env`, for examples see `src/app/.env.ci`

## Installing on a local machine
This project requires python3.6 and postgresql.

Install requirements:

```sh
cd src && pip install -r requirements.txt
cp app/.env.ci app/.env  # default environment variables
```

```sh
./manage.py migrate
./manage.py createsuperuser
```

Testing:
```bash
# run init tests
$ pytest
```

Development servers:

```bash
# run django dev server
$ ./manage.py runserver

```

## Backend Code requirements

### Style

* Obey [django's style guide](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/#model-style).
* Configure your IDE to use [flake8](https://pypi.python.org/pypi/flake8) for checking your python code. For running flake8 manualy, do `cd src && flake8`
* Prefer English over your native language in comments and commit messages.
* Commit messages should contain the unique id of issue they are linked to (refs #100500)
* Every model and a model method should have a docstring.

### Code organisation

* KISS and DRY.
* Obey [django best practices](http://django-best-practices.readthedocs.io/en/latest/index.html).
* Make models fat. **No logic is allowed within the views or templates**. Only models.
* Use PEP-484 [type hints](https://www.python.org/dev/peps/pep-0484/) when possible.
* Prefer composition and [GenericRelations](https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/) over inheritance.
* Prefer [Manager](https://docs.djangoproject.com/en/1.10/topics/db/managers/) methods over static methods.
* Do not use [signals](https://docs.djangoproject.com/en/1.10/topics/signals/) for business logic. Signals are good only for notification purposes.
* No l10n is allowed in python code, use [django translation](https://docs.djangoproject.com/en/1.10/topics/i18n/translation/).
