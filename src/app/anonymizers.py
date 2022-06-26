from axes.models import AccessAttempt, AccessLog
from django.contrib.admin.models import LogEntry as DjangoAdminLogEntry
from django.contrib.sessions.models import Session as DjangoSession
from hattori.base import BaseAnonymizer, faker
from rest_framework.authtoken.models import Token


class Cleanup:
    attributes = [
        ('fake-field-for-hattori-to-work', faker.email),
    ]

    def run(self, *args, **kwargs):
        count = self.get_query_set().all().delete()
        return count, count, 0


class TokenAnonymizer(Cleanup, BaseAnonymizer):
    model = Token


class AxesAccessLogAnonimizer(Cleanup, BaseAnonymizer):
    model = AccessLog


class AxesAccessAttemtAnonmizer(Cleanup, BaseAnonymizer):
    model = AccessAttempt


class DjangoAdminLogAnonymizer(Cleanup, BaseAnonymizer):
    model = DjangoAdminLogEntry


class DjangoSessionAnonymizer(Cleanup, BaseAnonymizer):
    model = DjangoSession
