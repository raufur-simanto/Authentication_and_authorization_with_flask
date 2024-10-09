from flask_restx import Api

from project.apis.auth import auth_namespace
from project.apis.posts import post_namespace
from project.apis.users import user_namespace

api = Api(version="2.0", title="Simple Rest Web Service")

api.add_namespace(auth_namespace, "/auth")
api.add_namespace(user_namespace, "/users")
api.add_namespace(post_namespace, "/posts")
