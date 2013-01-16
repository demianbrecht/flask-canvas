from os.path import abspath

from sys import path
path.append(abspath('.'))

from flask import Flask, g
try:
    from simplejson import dumps
except:
    from json import dumps

from flask_canvas import canvas_endpoint, install, request

app = Flask('canvas_example')
app.config.update({
    'DEBUG': True,
    'CANVAS_CLIENT_ID': '490478964327084',
    'CANVAS_CLIENT_SECRET': '5dca6b38781441431dfb8d0836e6f3b5',
    'CANVAS_REDIRECT_URI': 'https://apps.facebook.com/flask_canvas',
    'CANVAS_SCOPE': 'email',
})
install(app)

@app.route('/', methods=['GET'])
def home():
    return 'hallo'

@canvas_endpoint
@app.route('/canvas/', methods=['POST'])
def canvas():
    return '<p>%s</p><p>%s</p>' % (
        dumps(g.canvas_user),
        dumps(request('/me')))

if __name__ == '__main__':
    app.run()
