from celery import chain
from httpx import TransportError

from django.apps import apps
from django.conf import settings

from amocrm.client import AmoCRMClient
from amocrm.client.http import AmoCRMClientException
from amocrm.models import AmoCRMUser
from amocrm.services.access_token_getter import AmoCRMTokenGetterException
from amocrm.services.contacts.contact_creator import AmoCRMContactCreator
from amocrm.services.contacts.contact_to_customer_linker import AmoCRMContactToCustomerLinker
from amocrm.services.contacts.contact_updater import AmoCRMContactUpdater
from amocrm.services.orders.order_lead_creator import AmoCRMOrderLeadCreator
from amocrm.services.orders.order_lead_to_course_linker import AmoCRMOrderLeadToCourseLinker
from amocrm.services.orders.order_lead_updater import AmoCRMOrderLeadUpdater
from amocrm.services.orders.order_transaction_creator import AmoCRMOrderTransactionCreator
from amocrm.services.products.course_creator import AmoCRMCourseCreator
from amocrm.services.products.course_updater import AmoCRMCourseUpdater
from amocrm.services.products.product_groups_updater import AmoCRMProductGroupsUpdater
from app.celery import celery


def amocrm_enabled() -> bool:
    return settings.AMOCRM_BASE_URL != ""


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    acks_late=True,
)
def push_user_to_amocrm(user_id: int) -> None:
    tasks_chain = chain(
        _push_customer.si(user_id=user_id),
        _push_contact.si(user_id=user_id),
        _link_contact_to_user.si(user_id=user_id),
    )
    return tasks_chain.delay()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    acks_late=True,
)
def push_order_to_amocrm(order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(id=order_id)

    if hasattr(order, "amocrm_transaction"):
        return None

    if hasattr(order, "amocrm_lead"):
        chain(
            _link_course_to_lead.si(order_id=order_id),
            _push_lead.si(order_id=order_id),
            _push_transaction.si(order_id=order_id),
        ).delay()
    else:
        chain(
            _push_lead.si(order_id=order_id),
            _link_course_to_lead.si(order_id=order_id),
            _push_transaction.si(order_id=order_id),
        ).delay()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def push_product_groups() -> None:
    AmoCRMProductGroupsUpdater()()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def push_course(course_id: int) -> int:
    course = apps.get_model("products.Course").objects.get(id=course_id)
    if hasattr(course, "amocrm_course"):
        return AmoCRMCourseUpdater(amocrm_course=course.amocrm_course)()
    else:
        return AmoCRMCourseCreator(course=course)()


@celery.task(acks_late=True)
def push_all_products_and_product_groups() -> None:
    push_product_groups.apply_async(link=_push_all_courses.si())


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def enable_customers() -> None:
    client = AmoCRMClient()
    client.enable_customers()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def _push_customer(user_id: int) -> int:
    client = AmoCRMClient()
    user = apps.get_model("users.User").objects.get(id=user_id)
    if hasattr(user, "amocrm_user"):
        return client.update_customer(amocrm_user=user.amocrm_user)
    else:
        amocrm_id = client.create_customer(user=user)
        amocrm_user = AmoCRMUser.objects.create(user=user, amocrm_id=amocrm_id)
        return amocrm_user.amocrm_id


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def _push_contact(user_id: int) -> int:
    user = apps.get_model("users.User").objects.get(id=user_id)
    if hasattr(user, "amocrm_user_contact"):
        return AmoCRMContactUpdater(amocrm_user_contact=user.amocrm_user_contact)()
    else:
        return AmoCRMContactCreator(user=user)()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def _link_contact_to_user(user_id: int) -> None:
    user = apps.get_model("users.User").objects.get(id=user_id)
    AmoCRMContactToCustomerLinker(user=user)()


@celery.task(acks_late=True)
def _push_all_courses() -> None:
    courses = apps.get_model("products.Course").objects.all()
    for course in courses:
        push_course.delay(course_id=course.id)


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def _push_lead(order_id: int) -> int:
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    if hasattr(order, "amocrm_lead"):
        return AmoCRMOrderLeadUpdater(amocrm_lead=order.amocrm_lead)()
    else:
        return AmoCRMOrderLeadCreator(order=order)()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def _push_transaction(order_id: int) -> int | None:
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    return AmoCRMOrderTransactionCreator(order=order)()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def _link_course_to_lead(order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    return AmoCRMOrderLeadToCourseLinker(amocrm_lead=order.amocrm_lead)()
