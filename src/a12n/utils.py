import jwt
from rest_framework_jwt.settings import api_settings


def get_jwt(user) -> str:
    """Make JWT for given user"""
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)

    return jwt_encode_handler(payload)


def decode_jwt_without_validation(token: str) -> dict:
    return jwt.decode(token, options={'verify_signature': False}, algorithms=['HS256'])
