# encoding=utf8
from flask import Flask, render_template, request
from flask import jsonify
from flask import session as login_session
from flask import make_response
from flask.ext.httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httplib2
import json
import random
import string
import requests
import sys
from models import Base, User
reload(sys)
sys.setdefaultencoding('utf8')

# Initialization
auth = HTTPBasicAuth()
app = Flask(__name__)
engine = create_engine('sqlite:///paleKaleUsersOAuth.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Create a state token to prevent request forgery
# Store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('clientOAuth.html', STATE=state)


@app.route('/oauth/<string:provider>', methods=['POST'])
def login(provider):
    if provider == 'google':
        code = request.json.get('auth_code')
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(json.dumps(
                'Failed to upgrade the authorization code.', 401))
            response.headers['Content-Type'] = 'application/json'
            return response
        # Check if the access token is valid
        access_token = credentials.access_token
        print 'In gconnect access token is %s' % access_token
        url = ('https://www.googleapis.com/oauth2/v2/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 501)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Verify if that access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                    json.dumps("Token's user ID doesn't match given user ID."),
                    401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Verify that the access token is valid for this app.
        if result['issued_to'] != CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID doesn't match app's."), 401)
            print "Token's client ID doesn't match app's."
            response.headers['Content-Type'] = 'application/json'
            return response
        # Check if user is already logged in
        stored_access_token = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(
                json.dumps('Current user is already connected.'), 200)
            print "Current user already connected."
            print "Stored acces token now is %s" % stored_access_token
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id
        login_session['provider'] = 'google'

        print "Stored acces finally is %s" % login_session.get('access_token')

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        login_session['provider'] = 'google'

        userId = login_session.get('user_id')
        if not userId:
            try:
                user = session.query(User).filter_by(
                    email=login_session.get('email')).first()
                userId = user.id
            except:
                userId = None
        if userId is None:
            user = User(username=login_session['username'],
                        email=login_session['email'],
                        picture=login_session['picture'])
            session.add(user)
            session.commit()
            userId = user.id
        user = session.query(User).filter_by(id=userId).one()
        login_session['user_id'] = userId
        name = user.username
        print 'Hello %s, welcome to Pale Kale Salads & Smothies' % name

        # Make the token
        token = user.generate_auth_token(60)

        # Send back the token to the client
        return jsonify({'token': token.decode('ascii')})

    else:
        return 'Unrecognized Provider'

if __name__ == '__main__':
    app.secret_key = 'SUPER_SECRET_KEY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
