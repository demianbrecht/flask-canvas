from os.path import abspath

from sys import path
path.append(abspath('.'))

from flask import Flask, g
try:
    from simplejson import dumps
except:
    from json import dumps

import flask_canvas

app = Flask('canvas_example')
app.config.update({
    'DEBUG': True,
    'CANVAS_CLIENT_ID': '490478964327084',
    'CANVAS_CLIENT_SECRET': '5dca6b38781441431dfb8d0836e6f3b5',
    'CANVAS_REDIRECT_URI': 'https://apps.facebook.com/flask_canvas',
    'CANVAS_SCOPE': 'email',
})
flask_canvas.install(app)

@app.route('/canvas/', methods=['POST'])
def canvas():
    return dumps(g.canvas_user)

if __name__ == '__main__':
    app.run()
