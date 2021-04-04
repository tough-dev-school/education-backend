from rest_framework_jwt import views as jwt

from a12n.api.throttling import AuthAnonRateThrottle


class ObtainJSONWebTokenView(jwt.ObtainJSONWebTokenView):
    throttle_classes = [AuthAnonRateThrottle]


class RefreshJSONWebTokenView(jwt.RefreshJSONWebTokenView):
    throttle_classes = [AuthAnonRateThrottle]
