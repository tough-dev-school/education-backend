from rest_framework import serializers

from notion.page import NotionPage


class NotionPageSerializer(serializers.Serializer):
    def to_representation(self, page: NotionPage) -> dict:
        return {block.id: block.data for block in page.blocks}
