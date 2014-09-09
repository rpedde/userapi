import json
import os
import unittest
import userapi

from userapi.database import db


class UserApiTestCase(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'test.db')
        self.config_path = os.path.join(os.path.dirname(__file__), 'test.conf')

        with open(self.config_path, 'w') as f:
            f.write('SQLALCHEMY_DATABASE_URI = "sqlite:///%s"\n' % self.db_path)
            f.write('TESTING = True\n')

        # hack up some db initialization
        user_app = userapi.cli.create_app(config=self.config_path)
        db.app = user_app
        db.metadata.create_all(db.engine)

        self.app = user_app.test_client()

    def tearDown(self):
        os.unlink(self.db_path)
        os.unlink(self.config_path)

    def _create_user(self, user):
        resp = self.app.post('/users/%s' % user,
                             content_type='application/json',
                             data='{}')
        self.assertEqual(resp.status_code, 201)

    def _add_user_to_group(self, user, group):
        resp = self.app.get('/users/%s' % user)
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/groups/%s' % group)

        current_members = []
        if(resp.status_code == 404):
            resp = self.app.post('/groups/%s' % group)
            self.assertEqual(resp.status_code, 201)
        else:
            current_members = json.loads(resp.data)

        current_members.append(user)
        resp = self.app.put('/groups/%s' % group,
                            content_type='application/json',
                            data=json.dumps(current_members))
        self.assertEqual(resp.status_code, 200)

    def test_010_empty_db(self):
        """ Make sure we have an empty user list """
        resp = self.app.get('/users/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 0)

    def test_020_404_on_invalid_user(self):
        """ Make sure we 404 on invalid user """
        resp = self.app.get('/users/notauser')
        self.assertEqual(resp.status_code, 404)

    def test_030_add_user(self):
        """ Make sure we can add and retrieve a user """
        resp = self.app.post('/users/testuser', content_type='application/json',
                             data=json.dumps(dict(
                                 first_name='first',
                                 last_name='last')))

        self.assertEqual(resp.status_code, 201)

        # now pull it back and check it
        resp = self.app.get('/users/testuser')
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.data)
        self.assertEqual(data['userid'], 'testuser')
        self.assertEqual(data['first_name'], 'first')
        self.assertEqual(data['last_name'], 'last')

    def test_035_bad_json_on_add_user(self):
        """ Make sure bad json in create returns 400 """
        resp = self.app.post('/users/invalid', content_type='applicaton/json',
                             data='THIS IS NOT VALID JSON')
        self.assertEqual(resp.status_code, 400)


    def test_037_dup_user_409s(self):
        """ Make sure that adding a duplicate user returns 409 """
        resp = self.app.post('/users/user1', content_type='application/json',
                             data='{}')
        self.assertEqual(resp.status_code, 201)
        resp = self.app.post('/users/user1', content_type='application/json',
                             data='{}')
        self.assertEqual(resp.status_code, 409)

    def test_040_delete_user(self):
        """ Make sure we can delete users """
        self._create_user("user1")
        resp = self.app.delete('/users/user1')
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get('/users/user1')
        self.assertEqual(resp.status_code, 404)

    def test_050_delete_invalid_user(self):
        """ Make sure delete on invalid user 404s """
        resp = self.app.delete('/users/notauser')
        self.assertEqual(resp.status_code, 404)

    def test_060_update_group(self):
        """ Make sure can update groups """
        self._create_user("user1")
        resp = self.app.put('/users/user1', content_type='application/json',
                            data=json.dumps(dict(first_name='first',
                                                 last_name='last')))
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get('/users/user1')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['first_name'], 'first')
        self.assertEqual(data['last_name'], 'last')

    def test_070_updates_404(self):
        """ Make sure updates to bad users 404 """
        resp = self.app.put('/users/baduser', content_type='application/json',
                            data=json.dumps(dict(first_name='first',
                                                 last_name='last')))
        self.assertEqual(resp.status_code, 404)

    def test_100_add_group(self):
        """ Make sure we can add a group """
        resp = self.app.post('/groups/group1')
        self.assertEqual(resp.status_code, 201)
        resp = self.app.get('/groups/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 1)
        self.assertTrue('group1' in data)

    def test_110_add_dup_group(self):
        """ Make sure adding a duplicate group 409s """
        resp = self.app.post('/groups/group1')
        self.assertEqual(resp.status_code, 201)
        resp = self.app.post('/groups/group1')
        self.assertEqual(resp.status_code, 409)

    def test_120_del_group(self):
        """ Make sure we can delete a group """
        resp = self.app.post('/groups/group1')
        self.assertEqual(resp.status_code, 201)
        resp = self.app.delete('/groups/group1')
        self.assertEqual(resp.status_code, 200)

        # make sure it isn't the group list anymore
        resp = self.app.get('/groups/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue('group1' not in data)

    def test_130_del_group_invalid(self):
        """ Make sure deleting an invalid group 404s """
        resp = self.app.delete('/groups/invalid')
        self.assertEqual(resp.status_code, 404)

    def test_200_user_group_adds(self):
        """ Make sure groups are created on user adds """
        resp = self.app.post('/users/testuser', content_type='application/json',
                             data=json.dumps(dict(
                                 first_name='first',
                                 last_name='last',
                                 groups=['admin'])))

        self.assertEqual(resp.status_code, 201)

        # now pull it back and check it
        resp = self.app.get('/users/testuser')
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.data)
        self.assertEqual(data['userid'], 'testuser')
        self.assertEqual(data['first_name'], 'first')
        self.assertEqual(data['last_name'], 'last')
        self.assertItemsEqual(data['groups'], ['admin'])

        # verify the backref
        resp = self.app.get('/groups/admin')
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.data)
        self.assertItemsEqual(data, ['testuser'])

    def test_210_cascade_user_del(self):
        """ Make sure deleted users disappear from group membership """
        self._create_user('user1')
        self._add_user_to_group('user1', 'admin')
        self._add_user_to_group('user1', 'users')
        self._create_user('user2')
        self._add_user_to_group('user2', 'admin')

        resp = self.app.delete('/users/user1')
        self.assertEqual(resp.status_code, 200)

        # admin should just have user2 in it
        resp = self.app.get('/groups/admin')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertItemsEqual(data, ['user2'])

        # and users should be empty (404)
        resp = self.app.get('/groups/users')
        print resp.data
        self.assertEqual(resp.status_code, 404)

    def test_220_cascade_group_del(self):
        """ Make sure deleted groups disappear from users """
        self._create_user('user1')
        self._add_user_to_group('user1', 'admin')
        self._add_user_to_group('user1', 'users')
        self._create_user('user2')
        self._add_user_to_group('user2', 'admin')

        resp = self.app.delete('/groups/admin')
        self.assertEqual(resp.status_code, 200)

        # user1 should just be a member of users
        resp = self.app.get('/users/user1')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertItemsEqual(data['groups'], ['users'])

        # user2 shold be a member of no groups
        resp = self.app.get('/users/user2')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertItemsEqual(data['groups'], [])
