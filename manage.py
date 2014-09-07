#!/usr/bin/env python

import userapi

from flask.ext.script import Manager

from userapi.database import db


manager = Manager(userapi.cli.create_app)
manager.add_option('-c', dest='config', required=False)


# FIXME: need some migration stuff.  alembic, maybe?

@manager.command
def create_db():
    """Creates the necessary sqlalchemy database"""
    db.metadata.create_all(db.engine)


manager.run()
