from rest_framework import serializers

from magnets.models import EmailLeadMagnetCampaign


class EmailLeadMagnetCampaignStubSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLeadMagnetCampaign
        fields = [
            "slug",
        ]
