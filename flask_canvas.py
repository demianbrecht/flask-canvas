""" Flask extension for Facebook canvas-based applications
"""
import hmac

from base64 import urlsafe_b64decode as b64decode
from hashlib import sha256 # pylint: disable=E0611
try:
    from simplejson import loads
except ImportError:
    from json import loads
from urllib2 import urlopen

from flask import abort, current_app as app, g, request as flask_request

def install(app): # pylint: disable=W0621
    """ Installs the extension

    :param app: The ``Flask`` app to apply the extension to.
    """
    app.before_request(_before_request)

def request(path, data=None):
    """ Convenience Facebook request function. 

    Utility function to request resources via the graph API, with the
    format expected by Facebook.
    """
    return loads(urlopen('%s%s?access_token=%s' % (
        'https://graph.facebook.com',
        path,
        g.canvas_user['oauth_token'])).read(), data)

def canvas_route(view_fn):
    """ Decorator for canvas route 
    """
    setattr(view_fn, '_canvas', True)

def _has_authorized():
    """ Check current user permission set

    Checks the current user permission set against the one being requested
    by the application.
    """
    perms = request('/me/permissions')['data'][0].keys()
    return all(k in perms for k in app.config[
        'CANVAS_SCOPE'].split(','))

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

def _before_request():
    """ Called before the Flask request is processed

    Capture the request and redirect the user as needed. This function
    will either redirect the user for authorization, or will set
    ``g.canvas_user`` to the dict that Facebook POSTs us in the canvas
    request through the ``signed_request`` param.
    """

    try:
        if not app.view_functions[ #pylint: disable=W0212
                flask_request.endpoint]._canvas: 
            return
    except (KeyError, AttributeError):
        # either we're handling a non-view request (i.e. static files, or the
        # view function hasn't been registered as a canvas endpoint
        return

    if 'signed_request' not in flask_request.form:
        app.logger.error('signed_request not in request.form')
        abort(403)

    try:
        _, decoded_data = _decode_signed_user(
            *flask_request.form['signed_request'].split('.'))
    except ValueError as e: # pylint: disable=C0103
        app.logger.error(e.message)
        abort(403)

    if 'oauth_token' not in decoded_data:
        app.logger.info('unauthorized user, redirecting')
        return _authorize()

    g.canvas_user = decoded_data
    if not app.config.get('CANVAS_SKIP_AUTH_CHECK',
        False) and not _has_authorized():
        app.logger.info(
            'user does not have the required permission set. redirecting.')
        return _authorize()

    app.logger.info('all required permissions have been granted')
