import hmac

from base64 import urlsafe_b64decode as b64decode
from hashlib import sha256
try:
    from simplejson import loads
except ImportError:
    from json import loads

from flask import abort, current_app as app, g, request

def _decode(data):
    data += "=" * (len(data) % 4)
    return b64decode(data.encode('utf-8'))

def _before_request():
    if 'signed_request' not in request.form:
        app.logger.error('signed_request not in request.form')
        abort(403)

    encoded_sig, encoded_data = request.form['signed_request'].split('.')
    decoded_sig = _decode(encoded_sig)
    decoded_data = loads(_decode(encoded_data))

    if decoded_sig != hmac.new(app.config['CANVAS_CLIENT_SECRET'], 
        encoded_data, sha256).digest():
        app.logger.error('sig doesn\'t match hash')
        abort(403)

    app.logger.info('hash matches signature')
    if 'oauth_token' not in decoded_data:
        return '<script>window.top.location = %s?%s&%s&%s<script>'% (
            'https://www.facebook.com/dialog/oauth/',
            app.config['CANVAS_CLIENT_ID'],
            app.config['CANVAS_REDIRECT_URI'],
            app.config['CANVAS_SCOPE'])

    g.canvas_user = decoded_data

def install(app):
    app.before_request(_before_request)
