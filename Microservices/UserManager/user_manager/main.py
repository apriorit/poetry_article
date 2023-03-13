import os
import flask

app = flask.Flask(__name__)


@app.route('/api/user')
def create_user():
    return 'User created'


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=os.getenv('USER_MANAGER_PORT'))
