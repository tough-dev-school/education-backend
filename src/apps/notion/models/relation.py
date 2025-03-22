from tree_queries.models import TreeNode

from core.models import TimestampedModel, models


class MaterialLink(TimestampedModel): ...


class MaterialRelation(TreeNode):
    material = models.ForeignKey("notion.Material", related_name="+", on_delete=models.CASCADE)  # type: ignore
