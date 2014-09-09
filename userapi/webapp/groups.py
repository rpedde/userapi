import json

from flask import Blueprint, request, make_response
from flask.ext import restful

from userapi.database import db
from userapi.database.model import GroupModel

groups_bp = Blueprint('groups', __name__)
groups_api = restful.Api(groups_bp)


class Groups(restful.Resource):
    """ Group management class """

    @groups_api.representation('text/plain')
    def _plain(self, data, code, headers=None):
        resp = make_response(data, code)
        resp.headers.extend(headers or {})
        return resp

    """ Manage group membership """
    def get(self, groupid):
        """ get the members of the specified group

        Returns:
          200 - if group exists, plus json list of users
          404 - if group does not exist
        """
        group = GroupModel.query.get(groupid)
        if not group:
            return self._plain('Group not found', 404)

        if len(group.users) == 0:
            return self._plain('Group empty', 404)

        return group.users

    def delete(self, groupid):
        """ delete the specified group object

        Returns:
          200 - deleted
          404 - group not found
        """
        group = GroupModel.query.get(groupid)
        if not group:
            return self._plain('Group not found', 404)

        # we have some cascading deletes to do as well
        db.session.delete(group)
        db.session.commit()

        return self._plain('Deleted successfully', 200)

    def post(self, groupid):
        """ create group

        Returns:
          201 - group created
          409 - group exists
        """
        if GroupModel.query.get(groupid):
            return self._plain('Group exists', 409)

        new_group = GroupModel(groupid)

        db.session.add(new_group)
        db.session.commit()

        return self._plain('Added Successfully', 201)

    def put(self, groupid):
        """ update the membership list of a group

        Returns:
          200 - updated
          404 - group not found
          400 - invalid JSON or bad user specified
        """
        group = GroupModel.query.get(groupid)
        if not group:
            return self._plain('Group not found', 404)

        try:
            data = json.loads(request.data)
        except ValueError:
            return self._plain("Invalid json", 400)

        db.session.add(group)

        try:
            group.users = data
        except ValueError as e:
            db.session.rollback()
            return self._plain(
                'Error updating group membership: %s' % str(e), 400)

        db.session.commit()

        return self._plain('Updated Successfully', 200)


class GroupsList(restful.Resource):
    """ see the whole group list """
    def get(self):
        return [x.groupid for x in GroupModel.query.all()]


groups_api.add_resource(Groups, '/<string:groupid>')
groups_api.add_resource(GroupsList, '/')
