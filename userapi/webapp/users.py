import json

from flask import Blueprint, request
from flask.ext import restful
from sqlalchemy.exc import SQLAlchemyError

from userapi.database import db
from userapi.database.model import UserModel

users_bp = Blueprint('users', __name__)
users_api = restful.Api(users_bp)


class Users(restful.Resource):
    """ Manage a single user -- get, put, delete """
    def get(self, userid):
        """ return the user object

        Returns:
          200 - success, with user data in json body
          404 - user does not exist
        """

        keys = ['userid', 'first_name', 'last_name', 'groups']

        user = UserModel.query.get(userid)
        if not user:
            return 'User not found', 404

        # return only a subset of the user object keys
        return dict((key, getattr(user, key)) for key in keys)

    def delete(self, userid):
        """ delete the specified user object

        Returns:
          500 - internal sql alchemy error
          404 - user does not exist
          200 - success
        """
        user = UserModel.query.get(userid)
        if not user:
            return 'User not found', 404

        try:
            db.session.delete(user)
        except SQLAlchemyError as e:
            db.session.rollback()
            return 'Error deleting user', 500

        db.session.commit()

        return 'Deleted successfully', 200

    def post(self, userid):
        """ create user object

        Returns:
          400 - invalid json
          409 - object exists
          201 - created object
        """
        if UserModel.query.get(userid):
            return "User Exists", 409

        request.get_data()

        try:
            data = json.loads(request.data)
        except ValueError:
            return "Invalid json", 400

        first_name = '' if not 'first_name' in data else data['first_name']
        last_name = '' if not 'last_name' in data else data['last_name']

        new_user = UserModel(userid, first_name=first_name, last_name=last_name)

        try:
            db.session.add(new_user)
        except SQLAlchemyError as e:
            db.session.rollback()
            return 'Error creating user', 500

        db.session.commit()

        # now, add the groups, if specified
        if 'groups' in data:
            new_user.groups = data['groups']
            db.session.commit()

        return 'Added Successfully', 201

    def put(self, userid):
        """ update a user object

        Returns:
          200 - success
          400 - bad json
          404 - user not found
        """
        update_user = UserModel.query.get(userid)
        if not update_user:
            return 'User not found', 404

        try:
            data = json.loads(request.data)
        except ValueError:
            return 'Invalid JSON', 400

        db.session.add(update_user)
        try:
            for field in ['first_name', 'last_name', 'groups']:
                if field in data:
                    setattr(update_user, field, data[field])
        except SQLAlchemyError as e:
            db.session.rollback()
            return 'Error updating user', 500

        db.session.commit()
        return 'User updates', 200


class UsersList(restful.Resource):
    """ see the whole user list """
    def get(self):
        return [{userid: x.userid,
                 last_name: x.last_name,
                 first_name: x.first_name}
                for x in UserModel.query.all()]



users_api.add_resource(Users, '/<string:userid>')
users_api.add_resource(UsersList, '/')
