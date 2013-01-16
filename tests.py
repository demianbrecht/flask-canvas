from unittest import TestCase
from flask import Flask

import flask_canvas

class TestExtension(TestCase):
    def setUp(self):
        self.app = Flask('flask_canvas')

    def tearDown(self):
        pass

    def test_install(self):
        flask_canvas.install(self.app)
