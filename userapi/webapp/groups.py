import json

from flask import Blueprint, request
from flask.ext import restful

from userapi.database import db
from userapi.database.model import GroupModel

groups_bp = Blueprint('groups', __name__)
groups_api = restful.Api(groups_bp)


class Groups(restful.Resource):
    """ Manage group membership """
    def get(self, groupid):
        """ return the members of the specified group, or 404 if no group """
        group = GroupModel.query.get(groupid)
        if not group:
            return 'Group not found', 404

        if len(group.users) == 0:
            return 'Group empty', 404

        return group.users

    def delete(self, groupid):
        """ delete the specified group object, or 404 if not exist """
        group = GroupModel.query.get(groupid)
        if not group:
            return 'Group not found', 404

        # we have some cascading deletes to do as well
        db.session.delete(group)
        db.session.commit()

        return 'Deleted successfully', 200

    def post(self, groupid):
        """ create group or 409 if already exists """

        if GroupModel.query.get(groupid):
            return 'Group exists', 409

        new_group = GroupModel(groupid)

        db.session.add(new_group)
        db.session.commit()

        return 'Added Successfully', 201

    def put(self, groupid):
        """ update the membership list of a group """
        group = GroupModel.query.get(groupid)
        if not group:
            return 'Group not found', 404

        try:
            data = json.loads(request.data)
        except ValueError:
            return "Invalid json", 400

        db.session.add(group)

        try:
            group.users = data
        except ValueError as e:
            db.session.rollback()
            return 'Error updating group membership: %s' % str(e), 400

        db.session.commit()

        return 'Updated Successfully', 200


class GroupsList(restful.Resource):
    """ see the whole group list """
    def get(self):
        return [x.groupid for x in GroupModel.query.all()]


groups_api.add_resource(Groups, '/<string:groupid>')
groups_api.add_resource(GroupsList, '/')
