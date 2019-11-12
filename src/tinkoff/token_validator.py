import hashlib
import json

from django.conf import settings

from tinkoff.exceptions import TinkoffPaymentNotificationInvalidToken, TinkoffPaymentNotificationNoTokenPassed


class TinkoffNotificationsTokenValidator:
    def __init__(self, data: dict):
        self.initial_data = data

    def __call__(self) -> bool:
        token = self.extract_token()
        data = self.build_data()

        result = self.validate_data_for_token(data, token)
        if result is not True:
            raise TinkoffPaymentNotificationInvalidToken(self.initial_data)
        return result

    def extract_token(self) -> str:
        try:
            return self.initial_data['Token']
        except KeyError:
            raise TinkoffPaymentNotificationNoTokenPassed(self.initial_data)

    def build_data(self) -> dict:
        data = self.initial_data.copy()
        data.pop('Token')
        data['Password'] = settings.TINKOFF_TERMINAL_PASSWORD
        return data

    def validate_data_for_token(self, data: dict, token: str) -> bool:
        values = []
        for key in sorted(data):
            value = data[key]
            if not isinstance(value, str):
                value = json.dumps(value)
            values.append(value)
        concatenated_values = ''.join(values)

        hashed = hashlib.sha256(concatenated_values.encode('utf8'))
        hexdigest = hashed.hexdigest()
        return hexdigest == token
