import pytest

from chains.models import Progress

pytestmark = [pytest.mark.django_db]


def test_creating_progress_record(message, study):
    message.send(to=study)

    assert Progress.objects.filter(message=message, study=study).exists()
