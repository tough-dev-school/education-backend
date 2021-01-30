from ipware import get_client_ip


def real_ip_middleware(get_response):
    def middleware(request):
        request.META['REMOTE_ADDR'] = get_client_ip(request)[0]

        return get_response(request)

    return middleware
