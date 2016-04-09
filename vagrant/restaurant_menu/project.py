from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from database_helper import db_init
from database_helper import add_menu_item, edit_menu_item, delete_menu_item
from database_helper import get_menu_item, get_restaurant, get_restaurant_items
from database_helper import get_restaurants
app = Flask(__name__)
session = db_init()


@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = get_restaurants(session)
    return render_template('restaurants.html',
                           restaurants=restaurants)


@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
    restaurant = get_restaurant(session, restaurant_id)
    items = get_restaurant_items(session, restaurant)
    return render_template('menu.html',
                           restaurant=restaurant,
                           items=items)


@app.route('/restaurants/<int:restaurant_id>/menu/item/new',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = get_restaurant(session, restaurant_id)
    if request.method == 'POST':
        new_item = add_menu_item(session,
                                 restaurant,
                                 {'name': request.form['name'],
                                  'description': request.form['description'],
                                  'price': request.form['price'],
                                  'restaurant_id': restaurant_id})
        flash(new_item.name + ' added successfully.')
        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))
    else:
        return render_template('newMenuItem.html',
                               restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/menu/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, item_id):
    menu_item = get_menu_item(session, item_id)
    restaurant = get_restaurant(session, restaurant_id)
    if request.method == 'POST':
        edited_item = edit_menu_item(session, menu_item, request.form)
        flash(edited_item.name + ' edited successfully.')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html',
                               restaurant=restaurant,
                               item=menu_item)


@app.route('/restaurants/<int:restaurant_id>/menu/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, item_id):
    menu_item = get_menu_item(session, item_id)
    restaurant = get_restaurant(session, restaurant_id)
    if request.method == 'POST':
        item_deleted = delete_menu_item(session, menu_item)
        if item_deleted:
            flash('Item deleted successfully.')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant.id))
    else:
        return render_template('deleteMenuItem.html',
                               restaurant=restaurant,
                               item=menu_item)


# Restaurant menu API
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = get_restaurant(session, restaurant_id)
    items = get_restaurant_items(session, restaurant)
    return jsonify(MenuItems=[item.serialize for item in items])


@app.route('/restaurant/<int:restaurant_id>/menu/item/<int:item_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, item_id):
    menu_item = get_menu_item(session, item_id)
    return jsonify(MenuItem=menu_item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
