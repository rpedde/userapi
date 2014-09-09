from userapi.database import db


# set up a many-to-many intermediate table
usergroup = db.Table('usergroup',
                     db.Column('user_id',
                               db.Integer,
                               db.ForeignKey('users.id')),
                     db.Column('group_id',
                               db.Integer,
                               db.ForeignKey('groups.id')))


class UserModel(db.Model):
    """ SQLAlchemy user model """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    def __init__(self, userid, first_name='', last_name=''):
        self.userid = userid
        self.first_name = first_name
        self.last_name = last_name

    # If a user is created with group membership, find the group
    # or create it automatically.  This could as easily fail if
    # the group doesn't exist.
    def _get_or_create_group(self, group):
        res = GroupModel.query.filter_by(groupid=group).first()
        if not res:
            res = GroupModel(group)
        return res

    def _get_groups(self):
        return [x.groupid for x in self.groups_obj]

    def _set_groups(self, groups):
        while(self.groups_obj):
            del self.groups_obj[0]

        for group in groups:
            self.groups_obj.append(self._get_or_create_group(group))

    # make a synthetic property that looks and sets like a
    # list of group names
    groups = property(_get_groups, _set_groups)

    def __repr__(self):
        return '<User: %r>' % self.userid


class GroupModel(db.Model):
    """ SQLAlchemy group model """
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    groupid = db.Column(db.String(50), unique=True, nullable=False)

    # set up the m-t-m relationship
    users_obj = db.relationship('UserModel', secondary=usergroup,
                                backref=db.backref('groups_obj'))

    def __init__(self, groupid):
        self.groupid = groupid

    # unlike the user synthetic property, we'll raise if we try
    # and add a non-existent user to the group membership list
    def _get_user(self, user):
        res = UserModel.query.filter_by(userid=user).first()
        if not res:
            raise ValueError('Unknown user %s' % user)
        return res

    def _get_users(self):
        return [x.userid for x in self.users_obj]

    def _set_users(self, users):
        while(self.users_obj):
            del self.users_obj[0]

        for user in users:
            self.users_obj.append(self._get_user(user))

    # synthetic property that looks like a list of users in
    # the group.
    users = property(_get_users, _set_users)

    def __repr__(self):
        return '<Group: %r>' % self.groupid
