from dataclasses import dataclass

from django.db.transaction import atomic

from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.cache.lead_pipeline_id import get_pipeline_id
from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMOrderLead
from app.services import BaseService


@dataclass
class AmoCRMOrderLeadDeleter(BaseService):
    """
    Set lead as closed which is the only way to delete lead from amocrm
    and delete AmoCRMOrderLead
    """

    amocrm_lead: AmoCRMOrderLead

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.order = self.amocrm_lead.order

    @atomic
    def act(self) -> None:
        self.client.update_lead(
            lead_id=self.amocrm_lead.amocrm_id,
            status_id=self.closed_status_id,
            pipeline_id=self.pipeline_id,
            price=self.order.price,
            created_at=self.order.created,
        )
        self.amocrm_lead.delete()

    @property
    def pipeline_id(self) -> int:
        return get_pipeline_id(pipeline_name="b2c")

    @property
    def closed_status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="closed")
