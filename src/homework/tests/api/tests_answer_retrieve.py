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

    assert got['text'].startswith('<p><em>should be rendered'), f'"{got["text"]}" should start with "<p><em>should be rendered"'


def test_parent_answer(api, question, answer, another_answer):
    answer.parent = another_answer
    answer.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/')

    assert got['parent'] == str(another_answer.slug)


def test_answers_without_parents_do_not_have_this_field(api, question, answer):
    """Just to document weird behaviour of our API: we hide the parent field when it is empty"""
    answer.parent = None
    answer.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/')

    assert 'parent' not in got


def test_wrong_question(api, another_question, answer):
    api.get(
        f'/api/v2/homework/questions/{another_question.slug}/answers/{answer.slug}/',
        expected_status_code=404,
    )


def test_403_for_not_purchased_users(api, question, answer, purchase):
    purchase.setattr_and_save('paid', None)

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=403,
    )


def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, question, answer, purchase):
    purchase.setattr_and_save('paid', None)

    api.user.is_superuser = True
    api.user.save()

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, question, answer, purchase):
    purchase.setattr_and_save('paid', None)

    api.user.add_perm('homework.question.see_all_questions')

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_configurable_permissions_checking(api, question, answer, purchase, settings):
    purchase.setattr_and_save('paid', None)

    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = True

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_ok_for_answers_of_another_authors(api, question, answer, mixer):
    answer.author = mixer.blend('users.User')
    answer.save()

    api.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_no_anon(anon, question, answer):
    anon.get(
        f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/',
        expected_status_code=401,
    )
