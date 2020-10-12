import time

import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError

from backend.settings import SECRET_KEY


def create_auth_token(user_id, token_ttl):
    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {"iat": token_ttl, "id": str(user_id)}

    token = str(jwt.encode(payload, SECRET_KEY, headers=headers), "utf-8")
    return token


def parse_user_id_from_auth_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(decoded_token["id"])
    except (InvalidSignatureError, DecodeError):
        return


def is_auth_token_expired(token: str) -> bool:
    current_time = int(time.time())
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_jwt["iat"] > current_time
    except (InvalidSignatureError, DecodeError):
        return False
