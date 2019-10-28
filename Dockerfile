FROM gdml/django-base:1.0.9

ADD requirements.txt /

ENV STATIC_ROOT /var/lib/django-static
ENV DATABASE_URL sqlite:////var/lib/django-db


WORKDIR /srv
ADD src /srv/

RUN ./manage.py collectstatic --noinput

VOLUME /srv
VOLUME /var/lib/django-db

#HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/api/v1/healthchecks/postgresql/ --header "Host: parsa.gdml.ru" || exit 1

CMD uwsgi --master --http :8000 --module app.wsgi --workers 2 --threads 2 --harakiri 25 --max-requests 1000 --log-x-forwarded-for
