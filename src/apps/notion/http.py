import httpx
from django.conf import settings
from sentry_sdk import add_breadcrumb

from apps.notion.exceptions import HTTPError


def fetch(resource: str, request_body: dict) -> dict:
    """Query notion through our middleware"""
    add_breadcrumb(category="http", message=f"Sending notion request for {resource}", level="debug", data=request_body)

    client = httpx.Client(
        http2=True,
    )
    response = client.post(
        url=f"{settings.NOTION_MIDDLEWARE_URL}/v1/notion/{resource}/",
        headers={
            "content-type": "application/json",
        },
        json=request_body,
        timeout=settings.NOTION_MIDDLEWARE_TIMEOUT,
    )

    if response.status_code != 200:
        raise HTTPError(f"{response.http_version} error {response.status_code} fetching notion resouce {resource}: {response.text}")

    notion_response = response.json()

    add_breadcrumb(category="http", message=f"Got notion response for {resource}", level="debug", data=notion_response)

    return notion_response


def fetch_asset(url: str) -> bytes:
    """Fetch S3 notion asset through our middleware"""
    add_breadcrumb(category="http", message="Fetching notion asset", level="debug", data={url: url})

    client = httpx.Client(
        http2=True,
    )
    response = client.post(
        url=f"{settings.NOTION_MIDDLEWARE_URL}/v1/asset/",
        json={
            "url": url,
        },
        timeout=settings.NOTION_MIDDLEWARE_ASSET_FETCHING_TIMEOUT,
    )

    if response.status_code != 200:
        raise HTTPError(f"{response.http_version} error {response.status_code} fetching asset {url}: {response.text}")

    return response.content


__all__ = ["fetch", "fetch_asset"]
