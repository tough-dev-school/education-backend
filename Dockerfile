ARG PYTHON_VERSION

#
# Compile custom uwsgi, cuz debian's one is weird
#
FROM python:${PYTHON_VERSION}-slim-bookworm as uwsgi-compile
ENV _UWSGI_VERSION 2.0.22
RUN apt-get update && apt-get --no-install-recommends install -y build-essential wget && rm -rf /var/lib/apt/lists/*
RUN wget -O uwsgi-${_UWSGI_VERSION}.tar.gz https://github.com/unbit/uwsgi/archive/${_UWSGI_VERSION}.tar.gz \
  && tar zxvf uwsgi-*.tar.gz \
  && UWSGI_BIN_NAME=/uwsgi make -C uwsgi-${_UWSGI_VERSION} \
  && rm -Rf uwsgi-*


#
# Build poetry and export compiled dependecines as plain requirements.txt
#
FROM python:${PYTHON_VERSION}-slim-bookworm as deps-compile

WORKDIR /
COPY poetry.lock pyproject.toml /

# Version is taken from poetry.lock, assuming it is generated with up-to-date version of poetry
RUN pip install --no-cache-dir poetry==$(cat poetry.lock |head -n1|awk -v FS='(Poetry |and)' '{print $2}')
RUN poetry export --format=requirements.txt > requirements.txt


#
# Base image with django dependecines
#
FROM python:${PYTHON_VERSION}-slim-bookworm as base
LABEL maintainer="fedor@borshev.com"

LABEL com.datadoghq.ad.logs='[{"source": "uwsgi", "service": "django"}]'

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

ENV STATIC_ROOT /var/lib/django-static
ENV CELERY_APP=core.celery

ENV _WAITFOR_VERSION 2.2.3

RUN apt-get update \
  && apt-get --no-install-recommends install -y gettext locales-all tzdata git wait-for-it wget \
  && rm -rf /var/lib/apt/lists/*

COPY --from=uwsgi-compile /uwsgi /usr/local/bin/
RUN pip install --no-cache-dir --upgrade pip
COPY --from=deps-compile /requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /src
COPY src /src

ENV NO_CACHE=On
RUN ./manage.py compilemessages
RUN ./manage.py collectstatic --noinput
ENV NO_CACHE=Off

USER nobody

#
# Web worker image
#
FROM base as web
HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/api/v2/healthchecks/db/ --header "Host: app.tough-dev.school" || exit 1
CMD ./manage.py migrate && uwsgi --master --http :8000 --module core.wsgi --workers 2 --threads 2 --harakiri 25 --max-requests 1000 --log-x-forwarded-for

#
# Background processing image
#
FROM base as worker
HEALTHCHECK CMD celery -A ${CELERY_APP} inspect ping -d $QUEUE@$HOSTNAME
CMD celery -A ${CELERY_APP} worker -Q $QUEUE -c ${CONCURENCY:-2} -n "${QUEUE}@%h" --max-tasks-per-child ${MAX_REQUESTS_PER_CHILD:-50} --time-limit ${TIME_LIMIT:-900} --soft-time-limit ${SOFT_TIME_LIMIT:-45}

#
# Periodic scheduler image
#
FROM base as scheduler
ENV SCHEDULER_DB_PATH=/var/db/scheduler
USER root
RUN mkdir -p ${SCHEDULER_DB_PATH} && chown nobody ${SCHEDULER_DB_PATH}
VOLUME ${SCHEDULER_DB_PATH}
USER nobody
HEALTHCHECK NONE
CMD celery -A ${CELERY_APP} beat --pidfile=/tmp/celerybeat.pid --schedule=${SCHEDULER_DB_PATH}/celerybeat-schedule.db
