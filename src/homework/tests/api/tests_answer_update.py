import pytest
from datetime import datetime, timedelta, timezone

from homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30:12+03:00'),
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def answer_of_another_author(mixer, question, another_user):
    return mixer.blend('homework.Answer', question=question, author=another_user)


def test_changing_text(api, answer):
    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'})

    answer.refresh_from_db()

    assert answer.text == '*patched*'


def test_changing_text_updates_modified_time(api, answer):
    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'})

    answer.refresh_from_db()

    assert answer.modified == datetime(2032, 12, 1, 15, 30, 12, tzinfo=timezone(timedelta(hours=3)))


def test_405_for_put(api, answer):
    api.put(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'}, expected_status_code=405)


def test_only_answers_not_longer_then_30_minutes_may_be_edited(api, answer, freezer):
    freezer.move_to('2032-12-01 16:30+03:00')

    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'}, expected_status_code=403)


def test_answers_modified_within_last_30_minutes_may_be_updated(api, answer, freezer):
    freezer.move_to('2032-12-01 16:30+03:00')

    Answer.objects.update(modified='2032-12-01 16:24+03:00')

    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'}, expected_status_code=200)


@pytest.mark.xfail(reason='WIP: will add per-course permissions later')
@pytest.mark.usefixtures('_no_purchase')
def test_403_without_a_purchase(api, answer):
    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'}, expected_status_code=403)


def test_404_for_answer_of_another_author(api, answer_of_another_author):
    api.patch(f'/api/v2/homework/answers/{answer_of_another_author.slug}/', {'text': '*patched*'}, expected_status_code=404)


def test_changing_text_response(api, answer):
    got = api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'})

    assert got['src'] == '*patched*'
    assert '<em>patched</em>' in got['text']
