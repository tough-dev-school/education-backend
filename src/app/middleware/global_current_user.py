from app.current_user import set_current_user, unset_current_user


def set_global_user(get_response):
    def middleware(request):
        set_current_user(request.user)

        response = get_response(request)

        unset_current_user()

        return response

    return middleware
