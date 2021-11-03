from datetime import datetime
from typing import Tuple
from uuid import uuid4

import pytest
from django.core import management
from mixer.backend.django import mixer

from homework.models import Answer
from products.models import Course
from users.management.commands.merge_same_email_users import Command
from users.models import User

pytestmark = pytest.mark.django_db


johnnys_uuid = uuid4()


def link_data_to_user(user):
    # an ordinary user and his data
    johnny = User.objects.filter(username='johnny').first() \
        or mixer.blend('users.User', username='johnny')
    johnnys_answer = Answer.objects.filter(slug=johnnys_uuid).first() \
        or mixer.blend('homework.Answer', slug=johnnys_uuid, author=johnny)

    mixer.blend('a12n.PasswordlessAuthToken', user=user)
    mixer.blend('homework.Answer', author=user)

    # access to same answer - will not be merged
    mixer.blend('homework.AnswerAccessLogEntry', answer=johnnys_answer, user=user)  # UC answer user
    # check of the same answer - will not be merged
    mixer.blend('homework.AnswerCrossCheck', answer=johnnys_answer, checker=user)  # UC answer checker
    mixer.blend('magnets.LeadCampaignLogEntry', user=user)
    mixer.blend('orders.Order', user=user)
    mixer.blend('orders.Order', user=johnny, giver=user)

    # personal course, will be merged
    mixer.blend('studying.Study', student=user)  # UC student course

    # shared course, will not be merged
    shared_course = Course.objects.filter(name='the course').first() \
        or mixer.blend('products.Course', name='the course')
    mixer.blend('studying.Study', student=user, course=shared_course)  # UC student course


def create_user(**kwargs):
    u = User.objects.create(**kwargs)
    link_data_to_user(u)
    return u


def create_users_to_merge() -> Tuple[User, User, User]:
    first = create_user(
        username='Test@test.com',
        first_name='Имя-1',
        last_name='Фамилия-1',
        email='Test@test.com',
        date_joined=datetime(2000, 1, 1),
        subscribed=True,
        first_name_en='Name-1',
        last_name_en='Lastname-1',
        gender='male'
    )
    second = create_user(
        username='test@test.com',
        first_name='',
        last_name='Фамилия-2',
        email='test@test.com',
        date_joined=datetime(2000, 1, 2),
        subscribed=False,
        first_name_en='Name-2',
        last_name_en='',
        gender='female'
    )
    third = create_user(
        username='teST@test.com',
        first_name='Имя-3',
        last_name='',
        email='teST@test.com',
        date_joined=datetime(2000, 1, 3),
        subscribed=False,
        first_name_en='',
        last_name_en='',
        gender=''
    )
    return first, second, third


def test_command_works():
    create_users_to_merge()

    assert Command().duplicate_email_query().count() == 1  # 1 group of 3 duplicates

    management.call_command('merge_same_email_users')

    assert Command().duplicate_email_query().count() == 0  # no groups


def test_source_user_becomes_inactive():
    first, second, third = create_users_to_merge()

    cmd = Command()
    cmd.merge_user(source=second, target=third)
    assert not second.is_active


def test_source_user_changes_username_to_uuid():
    first, second, third = create_users_to_merge()

    cmd = Command()
    cmd.merge_user(source=second, target=third)
    assert second.username == second.uuid


def test_source_user_loses_relations():
    first, second, third = create_users_to_merge()

    cmd = Command()
    cmd.merge_user(source=second, target=third)

    assert second.passwordlessauthtoken_set.count() == 0
    assert second.answer_set.count() == 0
    assert second.leadcampaignlogentry_set.count() == 0
    assert second.order_set.count() == 0
    assert second.created_gifts.count() == 0


def test_target_user_takes_source_user_relations():
    first, second, third = create_users_to_merge()

    cmd = Command()
    cmd.merge_user(source=second, target=third)

    assert third.passwordlessauthtoken_set.count() == 2
    assert third.answer_set.count() == 2
    assert third.leadcampaignlogentry_set.count() == 2
    assert third.order_set.count() == 2
    assert third.created_gifts.count() == 2
    assert third.study_set.count() == 3


def test_source_user_preserves_duplicated_relations():
    first, second, third = create_users_to_merge()

    cmd = Command()
    cmd.merge_user(source=second, target=third)

    assert second.answeraccesslogentry_set.count() == 1
    assert second.answercrosscheck_set.count() == 1
    assert second.study_set.count() == 1


def test_target_user_populates_empty_properties():
    first, second, third = create_users_to_merge()

    cmd = Command()
    cmd.merge_user(source=first, target=third)

    assert third.last_name == first.last_name
    assert third.first_name_en == first.first_name_en
    assert third.last_name_en == first.last_name_en
    assert third.gender == first.gender
    assert third.subscribed is first.subscribed
    # ? assert third.password
    # ? assert third.last_login


def test_target_user_preserves_non_empty_properties():
    first, second, third = create_users_to_merge()
    first_name = third.first_name

    cmd = Command()
    cmd.merge_user(source=first, target=third)

    assert third.first_name == first_name
