import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "Gr@up7")
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 13

    # Local
    MONGO_SERVER_NAME = os.getenv("MONGO_SERVER_NAME", "localhost")
    MONGO_USER_NAME = os.environ.get("MONGO_USER_NAME", "admin")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "simanto")

    MONGO_URI = (
        "mongodb://"
        + MONGO_USER_NAME
        + ":"
        + MONGO_PASSWORD
        + "@"
        + MONGO_SERVER_NAME
        + ":27017/task4?authSource=admin"
    )
