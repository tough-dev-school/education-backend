import debug_toolbar
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from a12n.api.views import (
    ObtainJSONWebTokenViaPasswordlessToken, ObtainJSONWebTokenView, RefreshJSONWebTokenView, RequestPasswordLessToken)
from app.views import HomePageView
from homework.api.views import QuestionView
from homework.api.viewsets import AnswerViewSet
from magnets.api.views import EmailLeadMagnetCampaignView
from products.api.viewsets import BundleViewSet, CourseViewSet, RecordViewSet
from tinkoff.api.views import TinkoffCreditNotificationsView, TinkoffPaymentNotificationsView
from users.api.views import SelfView

router = routers.SimpleRouter()
router.register('courses', CourseViewSet)
router.register('records', RecordViewSet)
router.register('bundles', BundleViewSet)
router.register('homework/answers', AnswerViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
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
    path('__debug__/', include(debug_toolbar.urls)),
    path('', HomePageView.as_view()),
]
