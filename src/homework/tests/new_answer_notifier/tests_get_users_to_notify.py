import pytest

pytestmark = [pytest.mark.django_db]


def get_users_to_notify(notifier):
    return list(notifier.get_users_to_notify())


def test_answer_author_is_not_in_the_list(notifier, answer):
    notifier = notifier(answer)

    assert answer.author not in get_users_to_notify(notifier)


def test_non_parent_non_sibling_answer_author_is_not_in_the_list(notifier, another_answer, answer):
    notifier = notifier(answer)

    assert another_answer.author not in get_users_to_notify(notifier)


def test_parent_answer_author_is_in_the_list(notifier, answer, another_answer):
    answer.parent = another_answer
    answer.save()

    notifier = notifier(answer)

    assert another_answer.author in get_users_to_notify(notifier)


def test_sibling_answer_author_is_in_the_list(notifier, answer, another_answer, mixer):
    answer.parent = another_answer.parent = mixer.blend('homework.Answer')
    answer.save()
    another_answer.save()

    notifier = notifier(answer)

    assert another_answer.author in get_users_to_notify(notifier)


def test_parent_of_parent_answer_author_is_in_the_list(notifier, answer, another_answer, parent_of_another_answer):
    answer.parent = another_answer
    answer.save()

    notifier = notifier(answer)

    assert parent_of_another_answer.author in get_users_to_notify(notifier)


def test_author_is_excluded_event_if_he_is_in_answer_tree(notifier, answer, another_answer):
    answer.parent = another_answer
    answer.save()
    another_answer.author = answer.author
    another_answer.save()

    notifier = notifier(answer)

    assert answer.author not in get_users_to_notify(notifier)
