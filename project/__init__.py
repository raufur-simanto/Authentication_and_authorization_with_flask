import logging
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo

cors = CORS()
bcrypt = Bcrypt()
mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    with app.app_context():

        app_settings = os.environ.get("APP_SETTINGS", "project.config.BaseConfig")
        app.config.from_object(app_settings)
        app.logger.setLevel(logging.INFO)
        mongo.init_app(app)
        cors.init_app(app)
        bcrypt.init_app(app)

        from project.apis import api

        api.init_app(app)

        @app.shell_context_processor
        def ctx():
            return {"app": app}

        return app
