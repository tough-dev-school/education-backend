ARG PYTHON_VERSION=3.13

#
# Compile custom uwsgi, cuz debian's one is weird
#
FROM python:${PYTHON_VERSION}-slim-bookworm AS uwsgi-compile
ENV _UWSGI_VERSION=2.0.30
RUN apt-get update && apt-get --no-install-recommends install -y build-essential wget && rm -rf /var/lib/apt/lists/*
RUN wget --progress=dot:giga -O uwsgi-${_UWSGI_VERSION}.tar.gz https://github.com/unbit/uwsgi/archive/${_UWSGI_VERSION}.tar.gz \
  && tar zxvf uwsgi-*.tar.gz \
  && UWSGI_BIN_NAME=/uwsgi make -C uwsgi-${_UWSGI_VERSION} \
  && rm -Rf uwsgi-*


#
# Build poetry and export compiled dependecines as plain requirements.txt
#
FROM ghcr.io/astral-sh/uv:0.8.22-alpine AS deps-compile

WORKDIR /
COPY uv.lock pyproject.toml /

RUN uv export -o /requirements.txt

#
# Base image with django dependecines
#
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

ENV STATIC_ROOT=/var/lib/django-static
ENV CELERY_APP=core.celery

RUN apt-get update \
  && apt-get --no-install-recommends install -y gettext locales-all tzdata git wait-for-it wget \
  && rm -rf /var/lib/apt/lists/*

COPY --from=uwsgi-compile /uwsgi /usr/local/bin/
RUN pip install --no-cache-dir --upgrade pip==25.2
COPY --from=deps-compile /requirements.txt /
RUN pip install --no-cache-dir --root-user-action=ignore -r /requirements.txt

WORKDIR /src
COPY src /src

ARG RELEASE=unset
ENV RELEASE=$RELEASE

RUN NO_CACHE=On ./manage.py compilemessages \
  && ./manage.py collectstatic --noinput

USER nobody

RUN echo "Built for ${RELEASE}"

#
# Web worker image
#
FROM base AS web
HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/api/v2/healthchecks/db/ --header "Host: app.tough-dev.school" || exit 1
CMD ["sh", "-c", "./manage.py migrate && uwsgi --master --http :8000 --module core.wsgi --workers 2 --threads 2 --harakiri 25 --max-requests 1000 --buffer-size 8192 --log-x-forwarded-for --logformat '%(addr) - - [%(ltime)] \"%(method) %(uri) %(proto)\" %(status) %(size) \"%(referer)\" \"%(uagent)\"'"]

#
# Background processing image
#
FROM base AS worker
HEALTHCHECK CMD celery -A ${CELERY_APP} inspect ping -d $QUEUE@$HOSTNAME
CMD ["sh", "-c", "celery -A ${CELERY_APP} worker -Q $QUEUE -c ${CONCURENCY:-2} -n \"${QUEUE}@%h\" --max-tasks-per-child ${MAX_REQUESTS_PER_CHILD:-50} --time-limit ${TIME_LIMIT:-900} --soft-time-limit ${SOFT_TIME_LIMIT:-45}"]

#
# Periodic scheduler image
#
FROM base AS scheduler
ENV SCHEDULER_DB_PATH=/var/db/scheduler
USER root
RUN mkdir -p ${SCHEDULER_DB_PATH} && chown nobody ${SCHEDULER_DB_PATH}
VOLUME ${SCHEDULER_DB_PATH}
USER nobody
HEALTHCHECK NONE
CMD ["sh", "-c", "celery -A ${CELERY_APP} beat --pidfile=/tmp/celerybeat.pid --schedule=${SCHEDULER_DB_PATH}/celerybeat-schedule.db"]
