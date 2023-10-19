from dataclasses import dataclass
import hashlib
import json

from django.conf import settings

from apps.tinkoff.exceptions import TinkoffPaymentNotificationInvalidToken
from apps.tinkoff.exceptions import TinkoffPaymentNotificationNoTokenPassed
from core.services import BaseService

PAYLOAD_KEYS_EXCLUDED_FROM_SIGNATURE_VALIDATION = [
    "Token",
    "Data",
]


@dataclass
class TinkoffNotificationsTokenValidator(BaseService):
    payload: dict

    def act(self) -> bool:
        token = self.extract_token()
        data = self.get_data_for_signature_validation()

        result = self.validate_payload_for_token(data, token)
        if result is not True:
            raise TinkoffPaymentNotificationInvalidToken(self.payload)
        return result

    def extract_token(self) -> str:
        try:
            return self.payload["Token"]
        except KeyError:
            raise TinkoffPaymentNotificationNoTokenPassed(self.payload)

    def get_data_for_signature_validation(self) -> dict:
        data = self.payload.copy()
        for key in PAYLOAD_KEYS_EXCLUDED_FROM_SIGNATURE_VALIDATION:
            data.pop(key, None)

        data["Password"] = settings.TINKOFF_TERMINAL_PASSWORD
        return data

    def validate_payload_for_token(self, payload: dict, token: str) -> bool:
        values = []
        for key in sorted(payload):
            value = payload[key]
            if not isinstance(value, str):
                value = json.dumps(value)
            values.append(value)
        concatenated_values = "".join(values)

        hashed = hashlib.sha256(concatenated_values.encode("utf8"))
        hexdigest = hashed.hexdigest()
        return hexdigest == token
