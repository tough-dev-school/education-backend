import jwt


def decode_jwt_without_validation(token: str) -> dict:
    return jwt.decode(token, options={'verify_signature': False}, algorithms=['RS256'])
