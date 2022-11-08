import pytest
from mixer.backend.django import mixer

from users.models import User

pytestmark = pytest.mark.django_db


def test_merged_user_becomes_inactive(bob_a, bob_b, command):
    command.merge_user(source=bob_a, target=bob_b)

    assert not bob_a.is_active


def test_merged_user_changes_username_to_uuid(bob_a, bob_b, command):
    command.merge_user(source=bob_a, target=bob_b)

    assert bob_a.username == bob_a.uuid


def test_merged_user_has_email_lowered(bob_a, bob_b, command):
    command.merge_user(source=bob_a, target=bob_b)

    assert bob_a.email == bob_a.email.lower()


@pytest.mark.parametrize(('prop_name', 'prop_value', 'empty_value'), [
    ('first_name', 'Боб', ''),
    ('last_name', 'Бобов', ''),
    ('first_name_en', 'Bob', ''),
    ('last_name_en', 'McBob', ''),
    ('subscribed', True, False),
    ('gender', User.GENDERS.MALE, ''),
])
def test_target_user_populates_empty_property(bob_a, bob_b, command, prop_name, prop_value, empty_value):
    setattr(bob_a, prop_name, prop_value)
    bob_a.save()
    setattr(bob_b, prop_name, empty_value)
    bob_b.save()

    command.merge_user(source=bob_a, target=bob_b)

    assert getattr(bob_b, prop_name) == prop_value


@pytest.mark.parametrize(('prop_name', 'prop_value', 'empty_value'), [
    ('first_name', 'Боб', ''),
    ('last_name', 'Бобов', ''),
    ('first_name_en', 'Bob', ''),
    ('last_name_en', 'McBob', ''),
    ('subscribed', True, False),
    ('gender', User.GENDERS.MALE, ''),
])
def test_target_user_preserves_non_empty_property(bob_a, bob_b, command, prop_name, prop_value, empty_value):
    setattr(bob_a, prop_name, empty_value)
    bob_a.save()
    setattr(bob_b, prop_name, prop_value)
    bob_b.save()

    command.merge_user(source=bob_a, target=bob_b)

    assert getattr(bob_b, prop_name) == prop_value


@pytest.mark.parametrize(('model', 'rel_name'), [
    ('a12n.PasswordlessAuthToken', 'user'),
    ('homework.Answer', 'author'),
    ('magnets.LeadCampaignLogEntry', 'user'),
    ('orders.Order', 'user'),
    ('orders.Order', 'giver'),
])
def test_source_user_relation_merged_into_target_user(bob_a, bob_b, command, model, rel_name):
    bob_a_rel = mixer.blend(model, **{rel_name: bob_a})

    command.merge_user(bob_a, bob_b)

    bob_a_rel.refresh_from_db()
    assert getattr(bob_a_rel, rel_name) == bob_b


def test_source_user_preserves_duplicated_relation_answer_access_log_entry(bob_a, bob_b, command):
    answer = mixer.blend('homework.Answer')
    rel_a = mixer.blend('homework.AnswerAccessLogEntry', user=bob_a, answer=answer)
    mixer.blend('homework.AnswerAccessLogEntry', user=bob_b, answer=answer)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert rel_a.user == bob_a


def test_source_user_preserves_duplicated_relation_answer_cross_check(bob_a, bob_b, command):
    answer = mixer.blend('homework.Answer')
    rel_a = mixer.blend('homework.AnswerCrossCheck', checker=bob_a, answer=answer)
    mixer.blend('homework.AnswerCrossCheck', checker=bob_b, answer=answer)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert rel_a.checker == bob_a


def test_source_user_preserves_duplicated_relation_study(bob_a, bob_b, command):
    course = mixer.blend('products.Course')
    rel_a = mixer.blend('studying.Study', student=bob_a, course=course)
    mixer.blend('studying.Study', student=bob_b, course=course)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert rel_a.student == bob_a
