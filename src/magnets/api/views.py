from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from app.views import AnonymousAPIView
from app.viewsets import ValidationMixin
from magnets.api.validators import LeadValidator
from magnets.creator import LeadCreator
from magnets.models import EmailLeadMagnetCampaign


class EmailLeadMagnetCampaignView(AnonymousAPIView, ValidationMixin):
    """Create a amocrm_lead for amocrm_lead campaign"""

    validator_class = LeadValidator

    def post(self, request: Request, slug: str) -> Response:
        self.data = request.POST

        self._validate(self.data)

        self.create_lead()

        campaign = self.get_object()
        return Response({"ok": True, "message": campaign.success_message}, status=201)

    def get_object(self) -> EmailLeadMagnetCampaign:
        return get_object_or_404(EmailLeadMagnetCampaign, slug=self.kwargs["slug"])

    def create_lead(self) -> None:
        lead_creator = LeadCreator(
            name=self.data.get("name"),
            email=self.data["email"],
            campaign=self.get_object(),
        )
        return lead_creator()
