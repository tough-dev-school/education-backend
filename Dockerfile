FROM python:3.8-slim

VOLUME /var/lib/django-db
ENV DATABASE_URL sqlite:////var/lib/django-db/db.sqlite

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev locales-all gettext && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uwsgi==2.0.18
ADD requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /srv
ADD src/ /srv

RUN ./manage.py collectstatic
RUN ./manage.py compilemessages

CMD uwsgi --http :8000 --wsgi-file app/wsgi.py --master --process 4 --threads 2
