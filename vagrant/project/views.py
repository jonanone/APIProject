# encoding=utf8
from flask import Flask
from flask import jsonify

app = Flask(__name__)


@app.route('/api/v1/users')
def handle_users():
    return jsonify({'users': 'this are users'})


if __name__ == '__main__':
    app.secret_key = 'SUPER_SECRET_KEY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
