import uuid
from datetime import datetime

from flask import current_app as app

from project import mongo

mongodb = mongo.db

users = mongodb["users"]
posts = mongodb["posts"]


def signup(email, username, usertype, hashed_password):
    return users.insert_one(
        {
            "user_id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_on": datetime.now(),
            "usertype": usertype if usertype else "",
        }
    )


def get_user_by_email(email):
    return users.find_one({"email": email})


def get_user_by_username(username):
    return users.find_one({"username": username})


def get_user_by_user_id(user_id):
    return users.find_one({"user_id": user_id})


def get_user_count_by_email(email):
    return users.count_documents({"email": email})


def get_user_count_by_username(username):
    return users.count_documents({"username": username})


def get_all_users():
    return list(users.find({}).sort("created_at", -1))


def delete_user_by_id(user_id):
    result = users.delete_one({"user_id": user_id})
    if result.deleted_count > 0:
        app.logger.info(f"User with  {user_id} deleted successfully.")
        return "success"
    else:
        app.logger.info(f"No user found with id  {user_id}.")
        return "failed"


def update_user(data_dict):
    app.logger.info(f"document update payload: {data_dict}")
    user_id = data_dict.get("user_id")
    del data_dict["user_id"]

    for key, val in data_dict.items():
        users.update_one({"user_id": user_id}, {"$set": {key: val}})
    return True


def create_post(email, username, title):
    return posts.insert_one(
        {
            "post_id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "title": title,
            "created_on": datetime.now(),
        }
    )


def get_post_by_email(email):
    return posts.find_one({"email": email})


def get_post_by_post_id(post_id):
    return posts.find_one({"post_id": post_id})


def get_post_by_user(username):
    return posts.find_one({"username": username})


def update_post(data_dict):
    app.logger.info(f"document update payload: {data_dict}")
    post_id = data_dict.get("user_id")
    del data_dict["post_id"]

    for key, val in data_dict.items():
        posts.update_one({"post_id": post_id}, {"$set": {key: val}})
    return True


def get_all_posts():
    return list(posts.find({}).sort("created_at", -1))


def delete_post_by_id(post_id):
    result = posts.delete_one({"post_id": post_id})
    if result.deleted_count > 0:
        app.logger.info(f"User with  {post_id} deleted successfully.")
        return "success"
    else:
        app.logger.info(f"No post found with id  {post_id}.")
        return "failed"


def update_post(data_dict):
    app.logger.info(f"document update payload: {data_dict}")
    post_id = data_dict.get("post_id")
    del data_dict["post_id"]

    for key, val in data_dict.items():
        posts.update_one({"post_id": post_id}, {"$set": {key: val}})
    return True


def delete_post_by_id(post_id):
    result = posts.delete_one({"post_id": post_id})
    if result.deleted_count > 0:
        app.logger.info(f"Post with  {post_id} deleted successfully.")
        return "success"
    else:
        app.logger.info(f"No user found with id  {post_id}.")
        return "failed"
