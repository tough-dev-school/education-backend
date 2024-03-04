from apps.amocrm.client import http


class AmoCRMLeadNoteDTO:
    """https://www.amocrm.ru/developers/content/crm_platform/events-and-notes#notes-common-info"""

    def create_service_message(self, lead_id: int, service_name: str, note_text: str) -> int:
        data = {
            "note_type": "service_message",
            "params": {
                "service": service_name,
                "text": note_text,
            },
        }

        response_data = http.post(url=f"/api/v4/leads/{lead_id}/notes", data=[data])

        return response_data["_embedded"]["notes"][0]["id"]
