from django.urls import path

from magnets.api.views import EmailLeadMagnetCampaignView

urlpatterns = [
    path("email/<slug:slug>/", EmailLeadMagnetCampaignView.as_view()),
]
