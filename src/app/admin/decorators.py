from functools import wraps


def field(short_description=None, admin_order_field=None, boolean=None):
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):

            return fn(*args, **kwargs)

        if short_description is not None:
            decorated.short_description = short_description

        if admin_order_field is not None:
            decorated.admin_order_field = admin_order_field

        if boolean is not None:
            decorated.boolean = boolean

        return decorated

    return decorator
