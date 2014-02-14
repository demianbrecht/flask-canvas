""" Flask extension for Facebook canvas-based applications
"""
import hmac

from base64 import urlsafe_b64decode as b64decode
from hashlib import sha256 # pylint: disable=E0611
try:
    from simplejson import loads
except ImportError:
    from json import loads
from inspect import getargspec
from urllib2 import urlopen, Request

from flask import (Flask, abort, current_app as app, request as flask_request,
    redirect)


_ARG_KEY = 'canvas_user'


def install(app):
    """ Installs the Flask extension
    """
    Flask.canvas_route = _canvas_route
    app.logger.info('monkey patching complete')


class User(dict):
    def request(self, path, data=None, method='GET'):
        """ Convenience Facebook request function. 

        Utility function to request resources via the graph API, with the
        format expected by Facebook.
        """
        url = '%s%s?access_token=%s' % (
            'https://graph.facebook.com',
            path,
            self['oauth_token'])

        req = Request(url, data=data)
        req.get_method = lambda: method

        return loads(urlopen(req).read())

    def has_permissions(self):
        """ Check current user permission set

        Checks the current user permission set against the one being requested
        by the application.
        """
        perms = self.request('/me/permissions')['data'][0].keys()
        return all(k in perms for k in app.config[
            'CANVAS_SCOPE'].split(','))


def _canvas_route(self, *args, **kwargs):
    """ Decorator for canvas route 
    """
    def outer(view_fn):
        @self.route(*args, **kwargs)
        def inner(*args, **kwargs):
            fn_args = getargspec(view_fn)
            try:
                idx = fn_args.args.index(_ARG_KEY)
            except ValueError:
                idx = -1

            if idx > -1:
                if 'error' in flask_request.args:
                    return redirect('%s?error=%s' % (
                        self.config.get('CANVAS_ERROR_URI', '/'),
                        flask_request.args.get('error')))

                if 'signed_request' not in flask_request.form:
                    self.logger.error('signed_request not in request.form')
                    abort(403)

                try:
                    _, decoded_data = _decode_signed_user(
                        *flask_request.form['signed_request'].split('.'))
                except ValueError as e:
                    self.logger.error(e.message)
                    abort(403)

                if 'oauth_token' not in decoded_data:
                    app.logger.info('unauthorized user, redirecting')
                    return _authorize()

                user = User(**decoded_data)

                if not app.config.get('CANVAS_SKIP_AUTH_CHECK', False) \
                    and not user.has_permissions():
                    self.logger.info(
                        'user does not have the required permission set.')
                    return _authorize()

                self.logger.info('all required permissions have been granted')
                args = args[:idx - 1] + (user,) + args[idx:]

            return view_fn(*args, **kwargs)
        return inner
    return outer


def _decode(data):
    """ Decodes the Facebook signed_request parts
    """
    data += "=" * (len(data) % 4)
    return b64decode(data.encode('utf-8'))


def _authorize():
    """ Redirect the user to Facebook's authorization page

    You can't just 302 a user as the app is rendered in an iframe
    """
    return """<!DOCTYPE html>
    <html>
        <head>
            <script>
                var oauth = "https://www.facebook.com/dialog/oauth/?";
                oauth += "client_id=%s";
                oauth += "&redirect_uri=" + encodeURIComponent("%s");
                oauth += "&scope=%s";
                window.top.location = oauth;
            </script>
        </head>
    </html>""" % (app.config['CANVAS_CLIENT_ID'], 
        app.config['CANVAS_REDIRECT_URI'], 
        app.config['CANVAS_SCOPE'],)


def _decode_signed_user(encoded_sig, encoded_data):
    """ Decodes the ``POST``ed signed data
    """
    decoded_sig = _decode(encoded_sig)
    decoded_data = loads(_decode(encoded_data))

    if decoded_sig != hmac.new(app.config['CANVAS_CLIENT_SECRET'], 
        encoded_data, sha256).digest():
        raise ValueError("sig doesn't match hash")

    return decoded_sig, decoded_data
