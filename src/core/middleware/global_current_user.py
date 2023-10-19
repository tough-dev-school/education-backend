from core.current_user import set_current_user
from core.current_user import unset_current_user


def set_global_user(get_response):  # type: ignore
    def middleware(request):  # type: ignore
        set_current_user(request.user)

        response = get_response(request)

        unset_current_user()

        return response

    return middleware
