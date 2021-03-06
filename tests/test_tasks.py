# project/test_tasks.py

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import Task, User

TEST_DB = 'test_tasks.db'

class TasksTests(unittest.TestCase):

    # setup and teardown

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

    # helper methods
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
            password=bcrypt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

    def create_admin_user(self):
        new_user = User(
            name='Superman',
            email='admin@test.com',
            password=bcrypt.generate_password_hash('powerful'),
            role='admin'
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
    
    def test_logged_in_users_can_access_tasks_page(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword')
        self.login('user1234', 'userpassword')
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to log in first.', response.data)

    def test_users_can_add_tasks(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'New entry was successfully posted.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='',
            priority='1',
            posted_date='01/01/0001',
            status='1'
            ), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b'The task was marked as complete.', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('user5678', 'user5678@test.com', 'userpassword')
        self.login('user5678', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(b'The task was marked as complete.', response.data)
        self.assertIn(b'You can only update tasks that belong to you.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('user5678', 'user5678@test.com', 'userpassword')
        self.login('user5678', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn(b'The task was deleted.', response.data)
        self.assertIn(b'You can only delete tasks that belong to you.', response.data)

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'powerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn(b'The task was marked as complete.', response.data)

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('user1234', 'user1234@test.com', 'userpassword')
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'powerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_task_template_displays_logged_in_user_name(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword'
        )
        self.login('user1234', 'userpassword')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'user1234', response.data)

    def test_users_cannot_see_task_modify_links_for_open_tasks_not_created_by_them(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword'
        )
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register(
            'user5678', 'user5678@test.com', 'userpassword',
            'userpassword'
        )
        response = self.login('user5678', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Mark as Complete', response.data)
        self.assertNotIn(b'Delete', response.data)

    def test_users_cannot_see_task_modify_links_for_closed_tasks_not_created_by_them(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword'
        )
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.app.get('complete/1/', follow_redirects=True)
        self.logout()
        self.register(
            'user5678', 'user5678@test.com', 'userpassword',
            'userpassword'
        )
        response = self.login('user5678', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Delete', response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword'
        )
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_open_tasks(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword'
        )
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'powerful')
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_closed_tasks(self):
        self.register(
            'user1234', 'user1234@test.com', 'userpassword',
            'userpassword'
        )
        self.login('user1234', 'userpassword')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.app.get('complete/1/')
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'powerful')
        self.create_task()
        response = self.app.get('complete/2/', follow_redirects=True)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'delete/2/', response.data)


if __name__ == "__main__":
    unittest.main()