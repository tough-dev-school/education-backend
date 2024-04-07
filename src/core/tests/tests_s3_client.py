import pytest

from core.integrations.s3 import AppS3

pytestmark = [pytest.mark.django_db]


def test_client_init():
    client = AppS3().client

    assert "botocore.client.S3" in str(client.__class__)
