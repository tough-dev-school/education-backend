from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500, include
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from rest_framework import routers
from urllib.parse import urljoin

from a12n.api.views import (
    ObtainJSONWebTokenViaPasswordlessToken, ObtainJSONWebTokenView, RefreshJSONWebTokenView, RequestPasswordLessToken)
from app.views import HomePageView
from homework.api.views import QuestionView
from magnets.api.views import EmailLeadMagnetCampaignView
from products.api.viewsets import BundleViewSet, CourseViewSet, RecordViewSet
from tinkoff.api.views import TinkoffCreditNotificationsView, TinkoffPaymentNotificationsView
from users.api.views import SelfView

router = routers.SimpleRouter()
router.register('courses', CourseViewSet)
router.register('records', RecordViewSet)
router.register('bundles', BundleViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sentry-debug/', lambda request: 1 / 0),
    path('api/v2/banking/tinkoff-notifications/', TinkoffPaymentNotificationsView.as_view()),
    path('api/v2/banking/tinkoff-credit-notifications/', TinkoffCreditNotificationsView.as_view()),
    path('api/v2/leads/email/<slug:slug>/', EmailLeadMagnetCampaignView.as_view()),
    path('api/v2/users/me/', SelfView.as_view()),
    path('api/v2/auth/token/', ObtainJSONWebTokenView.as_view()),
    path('api/v2/auth/token/refresh/', RefreshJSONWebTokenView.as_view()),
    path('api/v2/auth/passwordless-token/request/<str:user_email>/', RequestPasswordLessToken.as_view()),
    path('api/v2/auth/passwordless-token/<uuid:token>/', ObtainJSONWebTokenViaPasswordlessToken.as_view()),
    path('api/v2/homework/questions/<uuid:slug>/', QuestionView.as_view()),
    path('api/v2/markdownx/', include('markdownx.urls')),
    path('api/v2/healthchecks/', include('django_healthchecks.urls')),
    path('api/v2/', include(router.urls)),
    path('', HomePageView.as_view()),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]


if not settings.DEBUG and not settings.CI:
    """Redirect users from the errors to the frontend"""
    def redir_to_the_frontend(error_code):
        return lambda request, *args, **kwargs: redirect(urljoin(settings.FRONTEND_URL, f'/error/?code={error_code}'))

    handler400 = redir_to_the_frontend(400)
    handler403 = redir_to_the_frontend(403)
    handler404 = redir_to_the_frontend(404)
    handler500 = redir_to_the_frontend(500)
