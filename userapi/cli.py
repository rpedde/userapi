# Provide the cli entrypoints

import os

from flask import Flask

from userapi.database import db
from userapi.webapp.users import users_bp
from userapi.webapp.groups import groups_bp


class DefaultConfig(object):
    BIND = "0.0.0.0"
    PORT = "5000"


def create_app(config=None):
    """entrypoint for running the web services as a command-line"""
    app = Flask("userapi")
    app.config.from_object("%s.DefaultConfig" % __name__)

    # register our blueprints
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(groups_bp, url_prefix='/groups')

    # if we passed a config, use it, else defaults
    if config is not None:
        app.config.from_pyfile(os.path.realpath(config))

    db.init_app(app)

    return app
