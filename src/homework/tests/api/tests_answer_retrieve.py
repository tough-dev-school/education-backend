import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.mark.freeze_time('2022-10-09 11:10+12:00')  # +12 hours kamchatka timezone
@pytest.mark.usefixtures('kamchatka_timezone')
def test_ok(api, answer, question):
    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got) == 8
    assert got['created'] == '2022-10-09T11:10:00+12:00'
    assert got['modified'] == '2022-10-09T11:10:00+12:00'
    assert got['slug'] == str(answer.slug)
    assert got['author']['uuid'] == str(api.user.uuid)
    assert got['author']['first_name'] == api.user.first_name
    assert got['author']['last_name'] == api.user.last_name
    assert got['question'] == str(question.slug)
    assert got['has_descendants'] is False
    assert 'text' in got
    assert 'src' in got


def test_has_descendants_is_true_if_answer_has_children(api, answer, another_answer):
    another_answer.parent = answer
    another_answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['has_descendants'] is True


def test_query_count_for_answer_without_descendants(api, answer, django_assert_num_queries):
    with django_assert_num_queries(6):
        api.get(f'/api/v2/homework/answers/{answer.slug}/')


def test_markdown(api, answer):
    answer.text = '*should be rendered*'
    answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['text'].startswith('<p><em>should be rendered'), f'"{got["text"]}" should start with "<p><em>should be rendered"'
    assert got['src'] == '*should be rendered*'


def test_non_root_answers_are_ok(api, answer, another_answer):
    answer.parent = another_answer
    answer.save()

    api.get(f'/api/v2/homework/answers/{answer.slug}/', expected_status_code=200)


def test_answers_with_parents_have_parent_field(api, question, answer, another_answer):
    """Just to document weird behavior of our API: the parent is showed for not root answers only."""
    answer.parent = another_answer
    answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert 'parent' in got


def test_403_for_not_purchased_users(api, answer, purchase):
    purchase.set_not_paid()

    api.get(
        f'/api/v2/homework/answers/{answer.slug}/',
        expected_status_code=403,
    )


def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, answer, purchase):
    purchase.set_not_paid()

    api.user.is_superuser = True
    api.user.save()

    api.get(
        f'/api/v2/homework/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, answer, purchase):
    purchase.set_not_paid()

    api.user.add_perm('homework.question.see_all_questions')

    api.get(
        f'/api/v2/homework/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_configurable_permissions_checking(api, answer, purchase, settings):
    purchase.set_not_paid()

    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = True

    api.get(
        f'/api/v2/homework/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_ok_for_answers_of_another_authors(api, answer, mixer):
    answer.author = mixer.blend('users.User')
    answer.save()

    api.get(
        f'/api/v2/homework/answers/{answer.slug}/',
        expected_status_code=200,
    )


def test_no_anon(anon, answer):
    anon.get(
        f'/api/v2/homework/answers/{answer.slug}/',
        expected_status_code=401,
    )
