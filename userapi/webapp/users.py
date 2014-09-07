import json

from flask import Blueprint, request
from flask.ext import restful

from userapi.database import db
from userapi.database.model import UserModel

users_bp = Blueprint('users', __name__)
users_api = restful.Api(users_bp)


class Users(restful.Resource):
    """ Manage a single user -- get, put, delete """
    def get(self, userid):
        """ return the user object, or 404 if it does not exist """
        user = UserModel.query.get(userid)
        if not user:
            return 'User not found', 404

        return {'userid': user.userid,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'groups': user.str_groups}

    def delete(self, userid):
        """ delete the specified user object, or 404 if not exist """
        user = UserModel.query.get(userid)
        if not user:
            return 'User not found', 404

        db.session.delete(user)
        db.session.commit()

        return 'Deleted successfully', 200

    def post(self, userid):
        """ create user object

        :return: 400 invalid json
        :return: 409 object exists
        :return: 201 created object """

        if UserModel.query.get(userid):
            return "User Exists", 409

        request.get_data()

        try:
            data = json.loads(request.data)
        except ValueError:
            return "Invalid json", 400

        new_user = UserModel(userid,
                             first_name='' if not 'first_name' in data else data['first_name'],
                             last_name='' if not 'last_name' in data else data['last_name'])

        db.session.add(new_user)
        db.session.commit()

        # now, add the groups, if specified
        if 'groups' in data:
            new_user.str_groups = data['groups']
            db.session.commit()

        return 'Added Successfully', 201


class UsersList(restful.Resource):
    """ see the whole user list """
    def get(self):
        return [{userid: x.userid, last_name: x.last_name, first_name: x.first_name} for x in UserModel.query.all()]



users_api.add_resource(Users, '/<string:userid>')
users_api.add_resource(UsersList, '/')
