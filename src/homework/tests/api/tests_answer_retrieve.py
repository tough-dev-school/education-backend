import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


def test_ok(api, question, answer):
    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/')

    assert got['slug'] == str(answer.slug)
    assert got['author']['first_name'] == api.user.first_name
    assert got['author']['last_name'] == api.user.last_name


def test_markdown(api, question, answer):
    answer.text = '*should be rendered*'
    answer.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/')

    assert '<em>should be rendered' in got['text']


def test_parent_answer(api, question, answer, another_answer):
    answer.parent = another_answer
    answer.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/')

    assert got['parent'] == str(another_answer.slug)


def test_wrong_question(api, mixer, answer):
    another_question = mixer.blend('homework.Question')

    api.get(
        f'/api/v2/homework/questions/{another_question.slug}/answers/{answer.slug}/',
        expected_status_code=404,
    )


def test_401_for_not_purchased_users(api, question, answer, purchase):
    purchase.setattr_and_save('paid', None)

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=403,
    )


def test_configurable_permissions_checking(api, question, answer, purchase, settings):
    purchase.setattr_and_save('paid', None)
    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = True

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_no_anon(anon, question, answer):
    anon.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=401,
    )
