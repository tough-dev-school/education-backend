FROM python:3.10.5-slim-buster as base
LABEL maintainer="fedor@borshev.com"

LABEL com.datadoghq.ad.logs='[{"source": "uwsgi", "service": "django"}]'

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

ENV STATIC_ROOT /var/lib/django-static
ENV CELERY_APP=app.celery

ENV _UWSGI_VERSION 2.0.20
ENV DOCKERIZE_VERSION v0.6.1

RUN echo deb http://deb.debian.org/debian buster contrib non-free > /etc/apt/sources.list.d/debian-contrib.list \
  && apt-get update \
  && apt-get --no-install-recommends install -y gettext locales-all wget imagemagick tzdata git \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get --no-install-recommends install -y build-essential libxml2-dev libxslt1-dev \
  && apt-get --no-install-recommends install -y libjpeg62-turbo-dev libjpeg-dev libfreetype6-dev libtiff5-dev liblcms2-dev libwebp-dev tk8.6-dev \
  && apt-get --no-install-recommends install -y libffi-dev libcgraph6 libgraphviz-dev libmagic-dev \
  && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
  && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
  && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN wget -O uwsgi-${_UWSGI_VERSION}.tar.gz https://github.com/unbit/uwsgi/archive/${_UWSGI_VERSION}.tar.gz \
  && tar zxvf uwsgi-*.tar.gz \
  && UWSGI_BIN_NAME=/usr/local/bin/uwsgi make -C uwsgi-${_UWSGI_VERSION} \
  && rm -Rf uwsgi-*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /src
COPY src /src

ENV NO_CACHE=On
RUN ./manage.py compilemessages
RUN ./manage.py collectstatic --noinput
ENV NO_CACHE=Off

USER nobody


FROM base as web
HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/api/v2/healthchecks/db/ --header "Host: app.tough-dev.school" || exit 1
CMD ./manage.py migrate && uwsgi --master --http :8000 --module app.wsgi --workers 2 --threads 2 --harakiri 25 --max-requests 1000 --log-x-forwarded-for


FROM base as worker
HEALTHCHECK CMD celery -A ${CELERY_APP} inspect ping -d $QUEUE@$HOSTNAME
CMD celery -A ${CELERY_APP} worker -Q $QUEUE -c ${CONCURENCY:-2} -n "${QUEUE}@%h" --max-tasks-per-child ${MAX_REQUESTS_PER_CHILD:-50} --time-limit ${TIME_LIMIT:-900} --soft-time-limit ${SOFT_TIME_LIMIT:-45}


FROM base as scheduler
ENV SCHEDULER_DB_PATH=/var/db/scheduler
USER root
RUN mkdir -p ${SCHEDULER_DB_PATH} && chown nobody ${SCHEDULER_DB_PATH}
VOLUME ${SCHEDULER_DB_PATH}
USER nobody
HEALTHCHECK NONE
CMD celery -A ${CELERY_APP} beat --pidfile=/tmp/celerybeat.pid --schedule=${SCHEDULER_DB_PATH}/celerybeat-schedule.db
