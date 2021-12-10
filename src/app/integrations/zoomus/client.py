from django.conf import settings

from app.integrations.zoomus.http import ZoomusClientHTTP
from app.integrations.zoomus.user import ZoomusUser
from users.models import User


class ZoomusNonOkResponseException(Exception):
    pass


class ZoomusRoomNotFoundException(Exception):
    pass


class ZoomusClient:
    def __init__(self) -> None:
        self.http = ZoomusClientHTTP(
            api_key=settings.ZOOMUS_API_KEY,
            api_secret=settings.ZOOMUS_API_SECRET,
        )

    def invite(self, webinar_id: str, user: User) -> dict:
        zoomus_user = ZoomusUser(user)

        return self.http.post(
            url=f'v2/webinars/{webinar_id}/registrants/',
            data=dict(zoomus_user),
            expected_status_code=201,
        )
