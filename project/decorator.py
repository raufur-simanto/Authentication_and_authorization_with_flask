from functools import wraps

from flask import abort
from flask import current_app as app
from flask import request

from project.utils import decode_auth_token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get("Authorization")
        if not auth_token:
            abort(401, "Token Required")
        elif auth_token:
            token = auth_token.split(" ")[1]
        payload = decode_auth_token(token)
        if payload == "expired":
            abort(401, "Expired Token")
        elif payload == "invalid":
            abort(401, "Invalid Token")
        setattr(decorated, "email", payload["email"])
        setattr(decorated, "usertype", payload["usertype"])
        return f(*args, **kwargs)

    return decorated
