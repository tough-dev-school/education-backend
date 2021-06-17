import debug_toolbar
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from app.views import HomePageView

api = [
    path('v2/', include('app.urls.v2')),
]

urlpatterns = [
    path('api/', include(api)),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', HomePageView.as_view()),
]
