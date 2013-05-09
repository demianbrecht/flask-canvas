from unittest import TestCase
from flask import Flask

import flask_canvas

class TestExtension(TestCase):
    def setUp(self):
        self.app = Flask('flask_canvas')
        self.app.config.update({
            'CANVAS_CLIENT_ID': 'client_id',
            'CANVAS_REDIRECT_URI': 'redirect_uri',
            'CANVAS_SCOPE': 'scope',
        })

    def tearDown(self):
        pass

    def test_install(self):
        self.assertFalse(hasattr(self.app, 'canvas_route'))
        flask_canvas.install(self.app)
        self.assertTrue(hasattr(self.app, 'canvas_route'))

    def test_redirect(self):
        with self.app.test_request_context('/'):
            self.assertTrue('facebook.com/dialog'
                in flask_canvas._authorize())
