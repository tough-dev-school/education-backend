from urllib.parse import urljoin

from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500, include
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from rest_framework import routers

from courses.api.viewsets import CourseViewSet, RecordViewSet
from onetime.api.views import TokenDownloadView
from users.api.views import UserView

router = routers.SimpleRouter()
router.register('courses', CourseViewSet)
router.register('records', RecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sentry-debug/', lambda request: 1 / 0),
    path('api/v2/users/<int:pk>/', UserView.as_view()),
    path('api/v2/download/<uuid:token>/', TokenDownloadView.as_view()),
    path('api/v2/healthchecks/', include('django_healthchecks.urls')),
    path('api/v2/', include(router.urls)),

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
