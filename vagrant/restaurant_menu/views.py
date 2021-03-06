# encoding=utf8
from flask import Flask, render_template, redirect, url_for, request
from flask import jsonify, flash, abort, g
from flask import session as login_session
from flask import make_response
from flask.ext.httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
import httplib2
import json
import random
import string
import requests

from database_helper import db_init
from database_helper import add_restaurant, edit_restaurant, delete_restaurant
from database_helper import add_menu_item, edit_menu_item, delete_menu_item
from database_helper import get_menu_item, get_restaurant
from database_helper import get_restaurants, get_restaurant_items
from database_helper import get_ordered_restaurants
from database_helper import createUser, getUserId, getUserById, getUserByEmail
from database_helper import getUserByUsername, addUser, getUserWithToken
from utils import findARestaurant

import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Initialization
auth = HTTPBasicAuth()
app = Flask(__name__)
session = db_init()
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Restaurant Menu APP API

@app.route('/restaurants', methods=['GET', 'POST'])
@auth.login_required
def all_restaurants_handler():
    if request.method == 'GET':
        if request.args.get('order_by'):
            ordering_attr = request.args.get('order_by', '')
            restaurants = get_ordered_restaurants(session, ordering_attr)
        else:
            restaurants = get_restaurants(session)
        return jsonify(restaurants=[
                restaurant.serialize for restaurant in restaurants
            ])
    if request.method == 'POST':
        if (request.args.get('location') and request.args.get('mealType')):
            location = request.args.get('location', '')
            mealType = request.args.get('mealType', '')
            restaurant_data = findARestaurant(mealType, location)
            print restaurant_data
            new_restaurant = add_restaurant(session, restaurant_data)
            return jsonify(restaurant=new_restaurant.serialize)
        else:
            response = make_response(json.dumps('Invalid request'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/restaurants/<int:restaurant_id>',
           methods=['GET', 'PUT', 'DELETE'])
def restaurant_handler(restaurant_id):
    if request.method == 'GET':
        restaurant = get_restaurant(session, restaurant_id)
        return jsonify(restaurant=restaurant.serialize)
    if request.method == 'PUT':
        edited_restaurant = edit_restaurant(session,
                                            restaurant_id,
                                            request.args)
        return jsonify(restaurant=edited_restaurant.serialize)
    if request.method == 'DELETE':
        restaurant = get_restaurant(session, restaurant_id)
        restaurant_deleted = delete_restaurant(session, restaurant)
        if restaurant_deleted:
            response = make_response(json.dumps('Restaurant deleted'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps('Error deleting restaurant'), 500)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/protected_resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


# User Management
@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if getUserByUsername(session, username) is not None:
        abort(400)  # existing user
    user = addUser(session, username, password)
    return jsonify({'username': user.username}), 201


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@auth.verify_password
def verify_password(username_or_token, password):
    # Check if is a token first
    user = getUserWithToken(session, username_or_token)
    if not user:
        user = getUserByUsername(session, username_or_token)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/oauth/<string:provider>', methods=['POST'])
def login(provider):
    if provider == 'google':
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        code = request.data
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
            # response = make_response(
            #     json.dumps('Current user is already connected.'), 200)
            print "Current user already connected."
            # print "Stored acces token now is %s" % stored_access_token
            # response.headers['Content-Type'] = 'application/json'
            return jsonify({'token': stored_access_token.decode('ascii')})
            # return response

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
            userId = getUserId(session, login_session.get('email'))
        if userId is None:
            userId = createUser(session, login_session)
        user = getUserById(session, userId)
        login_session['user_id'] = userId
        print 'Hello %s, welcome to Restaurant Menu APP' % user.name

        # Make the token
        token = user.generate_auth_token(600)

        # Send back the token to the client
        return jsonify({'token': token.decode('ascii')})

    else:
        return 'Unrecognized Provider'


# Login management

# Create a state token to prevent request forgery
# Store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("Current user is not connected")
        return redirect(url_for('all_restaurants_handler'))
    # Execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(
            json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid
        print result
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
# END GOOGLE CONNECT


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        if login_session['provider'] == 'facebook':
            # fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        response = make_response(
            json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('You were not logged in to begin with.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'SUPER_SECRET_KEY'
    app.debug = True
    # app.run(host='0.0.0.0', port=5000)
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
