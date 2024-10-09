import os
from datetime import datetime, timedelta

import jwt
from flask import current_app as app
from flask import request


def encode_auth_token(email, usertype, name, _id):
    try:
        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, seconds=3600),
            "iat": datetime.utcnow(),
            "sub": _id,
            "name": name,
            "email": email,
            "usertype": usertype,
        }
        token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

        app.logger.info(token)
        return token
    except Exception as e:
        return e


def decode_auth_token(token):
    app.logger.info(app.config.get("SECRET_KEY"))
    try:
        payload = jwt.decode(
            token, app.config.get("SECRET_KEY"), algorithms="HS256", verify=True
        )
        # app.logger.info(f"decoded value: {payload}")
        return payload
    except jwt.ExpiredSignatureError as e:
        return "expired"
    except jwt.InvalidTokenError as e:
        return "invalid"
