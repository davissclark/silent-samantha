import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

# The setUp() method tries to create an environment for the test that is close to that of a running app. It first creates an app configured for testing and activates its context. This step ensures that tests have access to current_app, like regular requests. Then it creates a brand-new database that the test can use when necessary.

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

# The database and the app context are removed in the tearDown() method.

    def test_app_exists(self):
        self.assertFalse(current_app is None)

# The first test ensures that the app instance exists.

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

# The second test ensures that the app is running under the testing configuration.