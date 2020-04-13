from django.conf import settings

from app.clickmeeting.http import ClickMeetingClientHTTP


class ClickMeetingNonOkResponseException(Exception):
    pass


class ClickMeetingRoomNotFoundException(Exception):
    pass


class ClickMeetingClient:
    def __init__(self):
        self.http = ClickMeetingClientHTTP(
            base_url='https://api.clickmeeting.com/v1/',
            api_key=settings.CLICKMEETING_API_KEY,
        )

    def invite(self, room_url: str, *args):
        conference = self.get_conference(room_url=room_url)
        if conference is None:
            raise ClickMeetingRoomNotFoundException(f'Room {room_url} not found')

        response = self.http.post(f'conferences/{conference["id"]}/invitation/email/ru', data={
            'attendees': [{'email': arg} for arg in args],
            'template': 'basic',
            'role': 'listener',
        })
        if response['status'] != 'OK':
            raise ClickMeetingNonOkResponseException(f'Non-OK response from ClickMeeting during invitation: {response["status"]}')

    def get_conference(self, **kwargs):
        response = self.http.get('conferences/')

        for conference in response['active_conferences']:
            if all(conference.get(key) == value for key, value in kwargs.items()):
                return conference
