# Noter
#
# copyright: (c) 2011 by Jon Staley.
# license: GPLv3, see LICENSE for more details.

import os
import noter
import unittest
import tempfile
import bcrypt

class NoterTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, noter.app.config['DATABASE'] = tempfile.mkstemp()
        noter.app.config['CSRF_ENABLED'] = False
        self.app = noter.app.test_client()
        noter.init_db()
        passwd = bcrypt.hashpw('default', bcrypt.gensalt())
        noter.create_user('admin@example.com', passwd)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(noter.app.config['DATABASE'])

    # helper functions

    def login(self, email, password):
        result = self.app.post('/login', data=dict(
            email=email,
            password=password), follow_redirects=True)

        return result

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # tests

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No notes found' in rv.data

    def test_login_logout(self):
        rv = self.login('admin@example.com', 'default')
        assert 'You are logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'Email/password incorrect ' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Email/password incorrect ' in rv.data

    def test_save_note(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='test note',
            entry='this is a test note',
            tags=''
        ), follow_redirects=True)
        assert 'No notes found' not in rv.data
        assert 'test note' in rv.data
        assert 'this is a test note' in rv.data

        rv = self.app.post('/view/1', data=dict(
            title='test note',
            entry='edit note',
            tags=''
        ), follow_redirects=True)
        assert 'test note' in rv.data
        assert 'this is a test note' not in rv.data
        assert 'edit note' in rv.data

    def test_remove_note(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='test note to remove',
            entry='this is a test note to remove',
            tags=''
        ), follow_redirects=True)
        assert 'test note to remove' in rv.data
        rv = self.app.get('/remove/1')
        assert 'test note to remove' not in rv.data

    def test_view_note(self):
        self.login('admin', 'default')
        self.app.post('/add', data=dict(
            title='spam',
            entry='eggs',
            tags='test, tag'), follow_redirects=True)
        rv = self.app.get('/view/1')
        assert 'spam' in rv.data
        assert 'eggs' in rv.data
        assert 'test' in rv.data
        assert 'tag' in rv.data

    def test_view_tags_notes(self):
        self.login('admin', 'default')
        self.app.post('/add', data=dict(
            title='first',
            entry='spam',
            tags='test, tag1'), follow_redirects=True)
        self.app.post('/add', data=dict(
            title='second',
            entry='eggs',
            tags='test, tag2'), follow_redirects=True)
        rv = self.app.get('/tag/test')
        assert 'first' in rv.data
        assert 'spam' in rv.data
        assert 'second' in rv.data
        assert 'eggs' in rv.data
        rv = self.app.get('/tag/tag1')
        assert 'first' in rv.data
        assert 'eggs' not in rv.data
        rv = self.app.get('/tag/tag2')
        assert 'second' in rv.data
        assert 'spam' not in rv.data


if __name__ == '__main__':
    unittest.main()
