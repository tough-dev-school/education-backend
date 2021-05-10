import pytest

pytestmark = [pytest.mark.django_db]


def test_answer_author_is_not_in_the_list(notifier, answer):
    notifier = notifier(answer)

    assert answer.author not in notifier.get_users_to_notify()


def test_parent_answer_author_is_in_the_list(notifier, answer, another_answer):
    answer.parent = another_answer
    answer.save()

    notifier = notifier(answer)

    assert another_answer.author in notifier.get_users_to_notify()


def test_parent_of_parent_answer_author_is_in_the_list(notifier, answer, another_answer, parent_of_another_answer):
    answer.parent = another_answer
    answer.save()

    notifier = notifier(answer)

    assert parent_of_another_answer.author in notifier.get_users_to_notify()


def test_author_is_excluded_event_if_he_is_in_answer_tree(notifier, answer, another_answer):
    answer.parent = another_answer
    answer.save()
    another_answer.author = answer.author
    another_answer.save()

    notifier = notifier(answer)

    assert answer.author not in notifier.get_users_to_notify()
