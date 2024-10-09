from flask import Flask, abort
from flask import current_app as app
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields

from project.cruds import (
    create_post,
    delete_post_by_id,
    delete_user_by_id,
    get_all_posts,
    get_all_users,
    get_post_by_user,
    get_user_by_email,
    get_user_by_user_id,
    get_user_by_username,
    update_user,
)
from project.decorator import token_required

user_namespace = Namespace("users")


user_model = user_namespace.model(
    "User",
    {
        "user_id": fields.String(description="User ID", readonly=True),
        "username": fields.String(required=True, description="User Name"),
        "usertype": fields.String(required=True, description="User Type"),
        "email": fields.String(required=True, description="email"),
        "created_on": fields.Raw(required=True, description="email"),
    },
)


# Upper-Level Resource 1: Users


class UserList(Resource):
    @token_required
    @user_namespace.response(200, "Get users data")
    @user_namespace.response(400, "Error in getting data")
    def get(self):
        """Get all users"""
        app.logger.info("Fetching all users")
        """Get all users with optional query parameters 'name' and 'limit'"""
        user_type = UserList.get.usertype
        app.logger.info(user_type)
        try:
            name = request.args.get("username")
            limit = request.args.get("limit", type=int)

            users = get_all_users()
            app.logger.info(f"users: {users}")

            filtered_users = users
            if name:
                filtered_users = [user for user in users if name in user["username"]]

            if limit:
                filtered_users = filtered_users[:limit]

            for user in filtered_users:
                user["_id"] = str(user["_id"])
                user["created_on"] = str(user["created_on"])

                del user["password"]

            resp_data = {"data": filtered_users, "msg": "success"}
            return resp_data, 200
        except Exception as e:
            return {"Error": e}, 400


class User(Resource):
    @token_required
    # @user_namespace.marshal_with(user_model)
    @user_namespace.response(404, "User not found")
    def get(self, user_id):
        """Get a specific user"""
        app.logger.info(f"Fetching user {user_id}")
        user_type = User.get.usertype
        user = get_user_by_user_id(user_id)
        if not user:
            app.logger.warning(f"404 Not Found: User {user_id} not found")
            abort(404, description=f"User with ID {user_id} not found")

        resp_data = {}
        resp_data["user_id"] = user["user_id"]
        resp_data["created_on"] = str(user["created_on"])
        resp_data["username"] = user["username"]
        resp_data["email"] = user["email"]

        return resp_data, 200

    @token_required
    @user_namespace.response(204, "User successfully deleted")
    def delete(self, user_id):
        """Delete a specific user"""
        app.logger.info(f"Deleting user {user_id}")
        user_type = getattr(self.delete, "usertype", None)
        app.logger.info(f"User type: {user_type}")

        if user_type.lower() != "admin":
            abort(400, "Not Authorized")

        user = get_user_by_user_id(user_id)
        if not user:
            app.logger.warning(f"404 Not Found: User {user_id} not found")
            abort(404, description=f"User with ID {user_id} not found")
        result = delete_user_by_id(user_id)
        app.logger.info(f"User {user_id} deleted")
        return "", 204

    @token_required
    @user_namespace.response(200, "User updated successfully")
    def put(self, user_id):
        """Update a specific user"""
        app.logger.info(f"Updating user {user_id}")
        payload = request.get_json()
        user = get_user_by_user_id(user_id)
        if not user:
            app.logger.warning(f"404 Not Found: User {user_id} not found")
            abort(404, description=f"User with ID {user_id} not found")
        payload["user_id"] = user_id

        if update_user(payload):
            user = get_user_by_user_id(user_id)
            resp_data = {}
            resp_data["user_id"] = user["user_id"]
            resp_data["created_on"] = str(user["created_on"])
            resp_data["username"] = user["username"]
            resp_data["email"] = user["email"]

            return resp_data, 200

        abort("Something went wrong", 400)


# # Nested Resource: Posts for a Specific User 1
class UserPosts(Resource):
    @token_required
    @user_namespace.response(404, "User not found")
    def get(self, user_id):
        """Get posts for a specific user"""
        app.logger.info(f"Fetching posts for user {user_id}")
        user = get_user_by_user_id(user_id)
        app.logger.info(f"user: {user}")
        if not user:
            app.logger.warning(f"404 Not Found: User {user_id} not found")
            abort(404, description=f"User with ID {user_id} not found")
        username = user["username"]
        posts = get_all_posts()
        user_posts = [post for post in posts if post["username"] == username]
        for post in user_posts:
            del post["_id"]
            post["created_on"] = str(post["created_on"])
        app.logger.info(f"Found posts for user {user_id}: {user_posts}")
        return user_posts, 200

    @token_required
    @user_namespace.response(201, "Post created successfully")
    def post(self, user_id):
        """Create a new post"""
        try:
            payload = request.get_json()
            user_email = getattr(self.post, "email", None)
            payload["email"] = user_email
            username = payload["username"]
            app.logger.info(f"payload: {payload}")
            user = get_user_by_user_id(user_id)
            if not user:
                return "No user found", 404
            username = user["username"]

            if get_user_by_username(username) and get_user_by_email(user_email):

                post = create_post(user_email, username, payload["title"])

                return {"msg": "post created successfully"}, 201
            else:
                abort(404, "No user found with this username")

        except Exception as e:
            abort(400, "Something went wrong")

    @token_required
    @user_namespace.response(204, "Post deleted successfully")
    def delete(self, user_id):
        """delete post"""
        try:
            email = getattr(self.delete, "email", None)
            usertype = getattr(self.delete, "usertype", None)

            user = get_user_by_user_id(user_id)
            if not user:
                return "No user found", 404
            username = user["username"]

            post = get_post_by_user(username)
            post_id = post["post_id"]

            if not post:
                app.logger.warning(f"404 Not Found")
                abort(404, description=f"Post not found")

            result = delete_post_by_id(post_id)
            app.logger.info(f"Post {post_id} deleted")
            return "", 204

        except Exception as e:
            abort(400, "Something went wrong")


# HATEOAS Example for User Resource
class UserLinks(Resource):
    @token_required
    def get(self, user_id):
        """Return HATEOAS links for a specific user"""
        app.logger.info(f"Fetching HATEOAS links for user {user_id}")
        user = get_user_by_user_id(user_id)
        if not user:
            app.logger.warning(f"404 Not Found: User {user_id} not found")
            abort(404, description=f"User with ID {user_id} not found")

        links = []
        links.append({"href": f"/users/{user_id}", "rel": "self"})
        links.append({"href": f"/users/{user_id}/posts", "rel": "posts"})
        user["links"] = links
        del user["_id"]
        del user["password"]
        user["created_on"] = str(user["created_on"])
        return user, 200


user_namespace.add_resource(UserList, "/")
user_namespace.add_resource(User, "/<string:user_id>")
user_namespace.add_resource(UserPosts, "/<string:user_id>/posts")
user_namespace.add_resource(UserLinks, "/<string:user_id>/links")
