import jwt
from rest_framework_jwt.utils import jwt_create_payload

from apps.users.models import User


def payload_handler(user: User) -> dict:
    """Add app-wide payload to generated JWT's"""
    return {
        **jwt_create_payload(user),
        "user_public_id": user.uuid,
    }


def decode_jwt_without_validation(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
