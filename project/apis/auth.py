import logging

from flask import current_app as app
from flask import request
from flask_restx import Namespace, Resource, fields

from project import bcrypt
from project.cruds import (
    get_user_by_email,
    get_user_count_by_email,
    get_user_count_by_username,
    signup,
)
from project.decorator import token_required
from project.utils import encode_auth_token

auth_namespace = Namespace("auth")

signup_model = auth_namespace.model(
    "signup",
    {
        "email": fields.String(required=True),
        "username": fields.String(required=True),
        "password": fields.String(required=True),
        "usertype": fields.String(required=True),
    },
)

login_model = auth_namespace.model(
    "login_model",
    {"email": fields.String(required=True), "password": fields.String(required=True)},
)

login_model_response = auth_namespace.model(
    "login_model_response",
    {
        "auth_token": fields.String(required=True),
        "message": fields.String(required=True),
    },
)

logout_response_model = auth_namespace.model(
    "logout_response_model",
    {
        "status": fields.String(required=True),
        "message": fields.String(required=True),
    },
)


class Signup(Resource):
    @auth_namespace.expect(signup_model, validate=True)
    @auth_namespace.response(200, "User signed up successfully.")
    @auth_namespace.response(
        409, "User with this username already exists. Please login."
    )
    @auth_namespace.response(409, "User with this email already exists. Please login.")
    @auth_namespace.response(400, "Please fill up all the fields.")
    def post(self):
        data = request.get_json()
        app.logger.info(f"payload: {data}")
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        usertype = data.get("usertype")
        if username and email and password and usertype:
            if get_user_count_by_email(email) <= 0:
                if get_user_count_by_username(username) <= 0:
                    hashed_password = bcrypt.generate_password_hash(
                        password, 13
                    ).decode()
                    app.logger.info(hashed_password)
                    signup(email, username, usertype, hashed_password)
                    return {"message": "User signed up successfully"}, 200
                else:
                    auth_namespace.abort(
                        409, f"User with this username already exists. Please login."
                    )
            else:
                auth_namespace.abort(
                    409, f"User with this email already exists. Please login."
                )
        else:
            auth_namespace.abort(400, f"Please fill up all the required fields")


class TokenValidation(Resource):
    @token_required
    @auth_namespace.response(200, "The Token is valid.")
    def get(self):
        type = TokenValidation.get.usertype
        app.logger.info(type)
        return {"message": f"This {type} token is valid."}, 200


class Login(Resource):
    @auth_namespace.marshal_with(login_model_response)
    @auth_namespace.expect(login_model, validate=True)
    @auth_namespace.response(401, "Wrong password.")
    @auth_namespace.response(404, "User doesn't exist.")
    @auth_namespace.response(400, "Please fill up all the fields.")
    def post(self):
        data = request.get_json()
        app.logger.info(f"**** PAYLOAD LOGIN {data} *****")
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = get_user_by_email(email)
            if user:
                isValid = bcrypt.check_password_hash(user["password"], password)
                if isValid:
                    name = user["username"]
                    _id = str(user["_id"])

                    auth_token = encode_auth_token(email, user["usertype"], name, _id)
                    app.logger.info(auth_token)
                    responseObject = {
                        "auth_token": auth_token,
                        "message": "Logged in successfully!",
                    }
                    return responseObject, 200
                else:
                    auth_namespace.abort(401, "Wrong password.")
            else:
                auth_namespace.abort(404, "User doesn't exist.")
        else:
            auth_namespace.abort(400, "Please fill up all the fields.")


class Logout(Resource):
    @token_required
    @auth_namespace.response(200, "Logout successfully")
    def get(self):
        response_object = {"status": "success", "message": "Successfully logged out!"}
        return response_object, 200


auth_namespace.add_resource(Signup, "/signup", endpoint="signup")
auth_namespace.add_resource(Login, "/login", endpoint="login")
auth_namespace.add_resource(Logout, "/logout", endpoint="logout")
auth_namespace.add_resource(TokenValidation, "/authenticate", endpoint="authenticate")
