import os
import noter
import unittest
import tempfile

class NoterTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, noter.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = noter.app.test_client()
        noter.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(noter.app.config['DATABASE'])

    # helper functions

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # tests

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No notes so far' in rv.data

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You are logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'Invalid username and password combination' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Invalid username and password combination' in rv.data

    def test_note(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='test note',
            entry='this is a test note',
            tags=''
        ), follow_redirects=True)
        assert 'No notes so far' not in rv.data
        assert 'test note' in rv.data
        assert 'this is a test note' in rv.data

if __name__ == '__main__':
    unittest.main()
