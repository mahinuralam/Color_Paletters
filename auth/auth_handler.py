# This file is responsible for signing , encoding , decoding and returning JWTS
import time
from typing import Dict

import jwt

JWT_SECRET = "use your secret code with secrets.token_hex(10)"
JWT_ALGORITHM = "HS256"

def token_response(token: str):
    print("TOEKNNNN -> ", token)
    return {
        "access_token": token
    }

# function used for signing the JWT string
def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print("TOEKNNNNN ------ ", decoded_token)
        return decoded_token
    except:
        return {}