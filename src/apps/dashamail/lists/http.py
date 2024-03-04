import httpx

from django.conf import settings

from apps.dashamail import exceptions


class DashamailListsHTTP:
    def call(self, method: str, payload: dict[str, str | int]) -> dict:
        response = httpx.post(
            url=f"https://api.dashamail.com/?method={method}&api_key={settings.DASHAMAIL_API_KEY}",
            json=payload,
        )

        response_json = self.get_json(response)

        if response.status_code != 200 or response_json is None:
            raise exceptions.DashamailWrongResponse(f"{response.status_code}: {response_json}")

        if response_json["response"]["msg"]["type"] == "error":
            raise exceptions.DashamailDirectCRMWrongResponse(f"Got dashamail error: {response_json['response']['msg']}")

        return response_json

    @staticmethod
    def get_json(response: httpx.Response) -> dict | None:
        if response.text:
            return response.json()
