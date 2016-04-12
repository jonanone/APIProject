from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from models import Base, Restaurant, MenuItem, User


# Init database session
def db_init():
    engine = create_engine('sqlite:///restaurantmenuwithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


# Get restaurants ordered alphabetically by name
def get_restaurants(session):
    all_restaurants = session.query(Restaurant).order_by(Restaurant.name)
    return all_restaurants


# Get restaurants ordered by given attribute
def get_ordered_restaurants(session, ordering_attr):
    all_restaurants = None
    if ordering_attr == 'name':
        all_restaurants = session.query(Restaurant).order_by(Restaurant.name)
    elif ordering_attr == 'id':
        all_restaurants = session.query(Restaurant).order_by(Restaurant.id)
    return all_restaurants


# Get restaurant by id
def get_restaurant(session, restaurant_id):
    return session.query(Restaurant).filter_by(id=restaurant_id).one()


# Add new restaurant
def add_restaurant(session, data):
    new_restaurant = Restaurant(name=data['name'])
    mapper = inspect(Restaurant)
    for key in data:
        for column in mapper.attrs:
            if key == column.key:
                setattr(new_restaurant, key, data[key])
    session.add(new_restaurant)
    session.commit()
    return new_restaurant


# Edit given restaurant
def edit_restaurant(session, restaurant_id, data):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    mapper = inspect(Restaurant)
    for key in data:
        for column in mapper.attrs:
            if key == column.key:
                setattr(restaurant, key, data[key])
    session.add(restaurant)
    session.commit()
    return restaurant


# Delete given restaurant
def delete_restaurant(session, restaurant):
    session.delete(restaurant)
    session.commit()
    return 1


# Get all restaurant items
def get_restaurant_items(session, restaurant):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return items


# Get menu item by id
def get_menu_item(session, menu_item_id):
    return session.query(MenuItem).filter_by(id=menu_item_id).one()


# Add new menu item
def add_menu_item(session, restaurant, data):
    new_item = MenuItem(name=data['name'],
                        description=data['description'],
                        price=data['price'],
                        course=data['course'],
                        restaurant_id=restaurant.id,
                        user_id=restaurant.user_id)
    session.add(new_item)
    session.commit()
    return new_item


# Edit menu item
def edit_menu_item(session, edited_item, data):
    mapper = inspect(MenuItem)
    for key in data:
        for column in mapper.attrs:
            if key == column.key and data[key]:
                setattr(edited_item, key, data[key])
    session.add(edited_item)
    session.commit()
    return edited_item


# Delete given menu item
def delete_menu_item(session, menu_item):
    session.delete(menu_item)
    session.commit()
    return 1


# User management
def addUser(session, username, password):
    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return user


def getUserByUsername(session, username):
    try:
        user = session.query(User).filter_by(username=username).one()
        return user
    except:
        return None


def getUserById(session, user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def getUserWithToken(session, token):
    user_id = User.verify_auth_token(token)
    if user_id:
        user = getUserById(session, user_id)
        return user
    else:
        return None


def createUser(session, login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    print 'User %s created succesfully' % user.name
    return user.id


def getUserId(session, email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def test():
    session = db_init()

    # Test get_restaurants
    restaurants = get_restaurants(session)
    print 'Restaurants loaded successfully.\n'
    for restaurant in restaurants:
        print restaurant.name
    print '--------------------'

    # Test add_restaurant
    new_restaurant = add_restaurant(session, {'name': 'Rocker\'s corner'})
    if new_restaurant:
        print new_restaurant.name + ' added successfully to the db.\n'
    print '--------------------'

    # Test edit_restaurant
    edited_restaurant = edit_restaurant(session, new_restaurant.id,
                                        {'name': 'Old rocker\'s corner'})
    if edited_restaurant:
        print edited_restaurant.name + ' edited successfully.\n'
    print '--------------------'

    # Test delete_restaurant
    restaurant_deleted = delete_restaurant(session, new_restaurant.id)
    if restaurant_deleted:
        print 'Restaurant deleted succesfully.\n'
        for restaurant in restaurants:
            print restaurant.name
    print '--------------------'
