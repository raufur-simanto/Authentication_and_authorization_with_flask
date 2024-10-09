from flask import Flask, abort
from flask import current_app as app
from flask import request
from flask_restx import Namespace, Resource, fields

from project.cruds import (
    create_post,
    delete_post_by_id,
    get_all_posts,
    get_post_by_post_id,
    get_user_by_email,
    get_user_by_user_id,
    get_user_by_username,
    update_post,
)
from project.decorator import token_required

post_namespace = Namespace("posts")


create_post_model = post_namespace.model(
    "Post",
    {
        "title": fields.String(required=True, description="Post Title"),
        "username": fields.String(required=True),
    },
)


class Posts(Resource):
    @post_namespace.response(200, "Get posts data")
    @post_namespace.response(400, "Error in getting data")
    def get(self):
        """Get all posts"""
        """Get all posts with optional query parameters 'username' and 'limit'"""
        try:
            name = request.args.get("username")
            limit = request.args.get("limit", type=int)

            posts = get_all_posts()
            app.logger.info(f"posts: {posts}")

            filtered_posts = posts
            if name:
                filtered_posts = [post for post in posts if name in post["username"]]

            if limit:
                filtered_posts = filtered_posts[:limit]

            for post in filtered_posts:
                post["created_on"] = str(post["created_on"])
                del post["_id"]

            resp_data = {"data": filtered_posts, "msg": "success"}
            return resp_data, 200
        except Exception as e:
            return {"Error": e}, 400

    @token_required
    @post_namespace.expect(create_post_model)
    @post_namespace.response(201, "Post created successfully")
    def post(self):
        """Create a new post"""
        try:
            payload = request.get_json()
            user_email = getattr(self.post, "email", None)
            payload["email"] = user_email
            username = payload["username"]
            app.logger.info(f"payload: {payload}")
            user = get_user_by_username(username)

            if get_user_by_username(username) and get_user_by_email(user_email):
                if user["email"] != user_email:
                    return "Not Authorized", 401

                post = create_post(user_email, username, payload["title"])

                return {"msg": "post created successfully"}, 201
            else:
                return "No user found with this username", 404

        except Exception as e:
            abort(400, "Something went wrong")


# Upper-Level Resource 2: Posts
class Post(Resource):
    @token_required
    @post_namespace.response(404, "User not found")
    def get(self, post_id):
        """Get a specific post"""
        app.logger.info(f"Fetching user {post_id}")
        post = get_post_by_post_id(post_id)
        if not post:
            app.logger.warning(f"404 Not Found")
            abort(404, description=f"Post with ID {post_id} not found")

        resp_data = {}
        resp_data["post_id"] = post["post_id"]
        resp_data["created_on"] = str(post["created_on"])
        resp_data["username"] = post["username"]
        resp_data["email"] = post["email"]

        return resp_data, 200

    @token_required
    @post_namespace.expect(create_post_model)
    @post_namespace.response(201, "Post created successfully")
    def put(self, post_id):
        """Update post"""
        try:
            email = getattr(self.put, "email", None)
            usertype = getattr(self.put, "usertype", None)
            payload = request.get_json()
            post = get_post_by_post_id(post_id)

            if not post:
                app.logger.warning(f"404 Not Found")
                abort(404, description=f"Post with ID {post_id} not found")

            if usertype != "admin":
                if post["email"] != email:
                    return "Not Authorized", 401

            payload["post_id"] = post_id

            if update_post(payload):
                post = get_post_by_post_id(post_id)
                resp_data = {}
                resp_data["post_id"] = post["post_id"]
                resp_data["created_on"] = str(post["created_on"])
                resp_data["username"] = post["username"]
                resp_data["email"] = post["email"]
                resp_data["title"] = post["title"]

                return resp_data, 200

            abort("Something went wrong", 400)
        except Exception as e:
            abort(400, "Something went wrong")

    @token_required
    @post_namespace.response(204, "Post deleted successfully")
    def delete(self, post_id):
        """delete post"""
        try:
            email = getattr(self.delete, "email", None)
            usertype = getattr(self.delete, "usertype", None)

            post = get_post_by_post_id(post_id)

            if not post:
                app.logger.warning(f"404 Not Found")
                abort(404, description=f"Post with ID {post_id} not found")

            if usertype != "admin":
                if post["email"] != email:
                    return "Not Authorized", 401

            result = delete_post_by_id(post_id)
            app.logger.info(f"Post {post_id} deleted")
            return "", 204

        except Exception as e:
            abort(400, "Something went wrong")


post_namespace.add_resource(Post, "/<string:post_id>")
post_namespace.add_resource(Posts, "/")
