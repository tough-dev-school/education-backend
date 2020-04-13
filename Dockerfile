FROM gdml/django-base:1.0.9

ADD requirements.txt /

ENV STATIC_ROOT /var/lib/django-static
ENV DATABASE_URL sqlite:////var/lib/django-db/pmdaily.sqlite
ENV CELERY_BACKEND redis://redis:6379/8


WORKDIR /srv
ADD src /srv/

RUN ./manage.py compilemessages
RUN ./manage.py collectstatic --noinput

VOLUME /srv
RUN mkdir /var/lib/django-db
VOLUME /var/lib/django-db

HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/api/v2/healthchecks/db/ --header "Host: edu-app.borshev.com" || exit 1

CMD ./manage.py migrate && uwsgi --master --http :8000 --module app.wsgi --workers 2 --threads 2 --harakiri 25 --max-requests 1000 --log-x-forwarded-for
