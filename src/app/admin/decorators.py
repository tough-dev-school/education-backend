from functools import wraps


def action(short_description=None):
    """Shortcut for setting actions with short description. Does not add it to actions, one has to do it manualy"""
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            return fn(*args, **kwargs)

        if short_description is not None:
            decorated.short_description = short_description

        return decorated

    return decorator


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
