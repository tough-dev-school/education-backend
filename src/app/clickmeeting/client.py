from django.conf import settings

from .http import ClickMeetingClientHTTP


class ClickMeetingNonOkResponseException(Exception):
    pass


class ClickMeetingClient:
    def __init__(self):
        self.http = ClickMeetingClientHTTP(
            base_url='https://api.clickmeeting.com/v1/',
            api_key=settings.CLICKMEETING_API_KEY,
        )

    def invite(self, room_id: str, *args):
        response = self.http.post(f'conferences/{room_id}/invitation/email/ru/', data={
            'attendees': args,
            'template': 'basic',
        })
        if response['status'] != 'OK':
            raise ClickMeetingNonOkResponseException(f'Non-OK response from ClickMeeting during invitation: {response["status"]}')
