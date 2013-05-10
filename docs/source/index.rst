.. contents::
   :depth: 3

Overview
--------

This extension deals with authentication for a Facebook canvas-based
application.

Installation
------------

From PyPI::

    pip install flask-canvas

From source::

    git clone git@bitbucket.org:demianbrecht/flask-canvas.git

Usage
-----

.. code-block:: python

    import flask_canvas

    # install will monkeypatch Flask in order to expose canvas_route
    flask_canvas.install(my_flask_app)

    # route your canvas-specific page
    @my_flask_app.canvas_route('/app', methods=['POST'])
    def canvas():
        return 'hello, world'

    # route page requiring user data
    @my_flask_app.canvas_route('/user', methods=['POST'])
    def user(canvas_user):
        return canvas_user.request('/me')

.. note:: 
   
   The user data parameter ``must`` be named ``canvas_user``.
   If a parameter with that name exists, the user data will be passed to
   it. Otherwise, it is ignored. Meaning that you can still have canvas
   views that don't receive user data (or incur overhead of parsing the
   ``signed_request`` payload.


Configuration
-------------

The following app configuration values may be set:

* ``CANVAS_CLIENT_ID``: Client ID supplied by Facebook
* ``CANVAS_REDIRECT_URI``: The redirect URI specified in your app settings
* ``CANVAS_CLIENT_SECRET``: Client secret supplied by Facebook
* ``CANVAS_SCOPE``: Resources application requires access to
* ``CANVAS_ERROR_URI`` (optional, default: ``"/"``: 
  Where the user is redirected to on auth error (cancel)
* ``CANVAS_SKIP_AUTH_CHECK`` (optional, default: ``False``): 
  Useful if your application never changes the
  scope requested. If ``True``, this will eliminate an extra request to the
  graph API to ensure that the users' current permission set matches a
  potentially updated list.


API
---
.. automodule:: flask_canvas
   :members:
   :undoc-members:
   :private-members:
