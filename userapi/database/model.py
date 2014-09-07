from userapi.database import db


usergroup = db.Table('usergroup',
                     db.Column('userid',
                               db.String(50),
                               db.ForeignKey('users.userid')),
                     db.Column('groupid',
                               db.String(50),
                               db.ForeignKey('groups.groupid')))


class UserModel(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    def __init__(self, userid, first_name='', last_name=''):
        self.userid = userid
        self.first_name = first_name
        self.last_name = last_name

    def _get_or_create_group(self, group):
        res = GroupModel.query.get(group)
        if not res:
            res = GroupModel(group)
        return res

    def _get_groups(self):
        return [x.groupid for x in self.groups]

    def _set_groups(self, groups):
        while(self.groups):
            del self.groups[0]

        for group in groups:
            self.groups.append(self._get_or_create_group(group))

    str_groups = property(_get_groups, _set_groups)

    def __repr__(self):
        return '<User: %r>' % self.userid


class GroupModel(db.Model):
    __tablename__ = 'groups'
    groupid = db.Column(db.String(50), primary_key=True)
    users = db.relationship('UserModel', secondary=usergroup,
                             backref=db.backref('groups'))

    def __init__(self, groupid):
        self.groupid = groupid

    def _get_user(self, user):
        res = UserModel.query.get(user)
        if not res:
            RaiseValueError('Unknown user %s' % user)
        return res

    def _get_users(self):
        return [x.userid for x in self.users]

    def _set_users(self, users):
        while(self.users):
            del self.users[0]

        for user in users:
            self.users.append(self._get_user(user))

    str_users = property(_get_users, _set_users)

    def __repr__(self):
        return '<Group: %r>' % self.groupid
