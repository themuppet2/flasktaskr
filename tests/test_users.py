# project/test_users.py

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import Task, User

TEST_DB = 'test_users.db'

class UsersTests(unittest.TestCase):

    ######## setup and teardown #########

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ####### helper methods #######
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name,
            password=password), follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('register/', data=dict(name=name,
            email=email, password=password, confirm=confirm),
        follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(
            name=name,
            email=email,
            password=bcyrpt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='02/03/2017',
            priority='1',
            posted_date='01/01/0001',
            status='1'
            ), follow_redirects=True)

    ########## TESTS ##########
    # each test should start with 'test'
    def test_users_can_register(self):
        new_user = User("testuser", "testuser@test.com", "testpassword")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "testuser"

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list', response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register(
            'user1234', 'user1234@test.com',
            'userpassword', 'userpassword')
        response = self.login('user1234', 'userpassword')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        self.register(
            'user1234', 'user1234@test.com',
            'userpassword', 'userpassword')
        response = self.login('alert("alert box!";','foo')
        self.assertIn(b'Invalid username or password.',
            response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)

    def test_user_registration(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword')
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_user_registration_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword')
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword')
        self.assertIn(b'That username and/or email already exist.',
            response.data)

    def test_logged_in_users_can_logout(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword')
        self.login('user1234', 'userpassword')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye!', response.data)

    def test_default_user_role(self):
        db.session.add(
            User(
                'Johnny',
                'john@doe.com',
                'johnny'
            )
        )
        db.session.commit()
        users = db.session.query(User).all()
        print(users)
        for user in users:
            self.assertEqual(user.role, 'user')


if __name__ == "__main__":
    unittest.main()