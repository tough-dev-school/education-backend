import debug_toolbar
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from a12n.api import views as a12n
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
    path('api/v2/auth/token/', a12n.ObtainJSONWebTokenView.as_view()),
    path('api/v2/auth/token/refresh/', a12n.RefreshJSONWebTokenView.as_view()),
    path('api/v2/auth/passwordless-token/request/<str:user_email>/', a12n.RequestPasswordLessToken.as_view()),
    path('api/v2/auth/passwordless-token/<uuid:token>/', a12n.ObtainJSONWebTokenViaPasswordlessToken.as_view()),
    path('api/v2/auth/as/<int:user_id>/', a12n.ObtainJSONWebTokenViaUserId.as_view()),
    path('api/v2/homework/questions/<uuid:slug>/', QuestionView.as_view()),
    path('api/v2/markdownx/', include('markdownx.urls')),
    path('api/v2/healthchecks/', include('django_healthchecks.urls')),
    path('api/v2/', include(router.urls)),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', HomePageView.as_view()),
]
