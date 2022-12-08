from django_filters import filters


class UUIDInFilter(filters.BaseInFilter, filters.UUIDFilter):
    """
    Gets comma separated UUID from GET parameter and matches entities by `in` operator.

    Example: url.com?some_slugs=003c1a63-5e62-43d4-a7f9-f7ec96a67998,f65b1003-ca9f-4051-9c63-8dbeaa9d838d
    """
