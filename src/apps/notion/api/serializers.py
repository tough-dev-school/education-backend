from rest_framework import serializers

from apps.notion.page import NotionPage


class NotionPageSerializer(serializers.Serializer):
    def to_representation(self, page: NotionPage) -> dict:
        return {block.id: block.get_data() for block in page.blocks}
