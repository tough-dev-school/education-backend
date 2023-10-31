from django.urls import path

from apps.magnets.api.views import EmailLeadMagnetCampaignView

urlpatterns = [
    path("email/<slug:slug>/", EmailLeadMagnetCampaignView.as_view()),
]
