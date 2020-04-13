from django.conf import settings

from app.zoomus.http import ZoomusClientHTTP
from app.zoomus.user import ZoomusUser
from users.models import User


class ZoomusNonOkResponseException(Exception):
    pass


class ZoomusRoomNotFoundException(Exception):
    pass


class ZoomusClient:
    def __init__(self):
        self.http = ZoomusClientHTTP(
            api_key=settings.ZOOMUS_API_KEY,
            api_secret=settings.ZOOMUS_API_SECRET,
        )

    def invite(self, webinar_id, user: User):
        user = ZoomusUser(user)

        return self.http.post(
            url=f'v2/webinars/{webinar_id}/registrants/',
            data=dict(user),
            expected_status_code=201,
        )
