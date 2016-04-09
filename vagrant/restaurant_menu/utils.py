import sys
import codecs
from geocode import getGeocodeLocation
from foursquare_helper import findNearbyRestaurantsByMealType
from foursquare_helper import getVenuePhotos
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


def findARestaurant(mealType, location):
    latitude, longitude = getGeocodeLocation(location)
    venues = findNearbyRestaurantsByMealType(latitude, longitude, mealType)
    if venues['response']['venues']:
        restaurant = venues['response']['venues'][0]
        photos = getVenuePhotos(restaurant['id'])
        image = 'http://i.imgur.com/HbnOnmFl.jpg'
        if photos and photos['response']['photos']['count'] > 0:
            first_photo = photos['response']['photos']['items'][0]
            prefix = first_photo['prefix']
            suffix = first_photo['suffix']
            image = prefix + '300x300' + suffix
        name = restaurant['name']
        print 'Restaurant Name: ' + name
        formattedAddress = restaurant['location']['formattedAddress']
        address = ''
        for item in formattedAddress:
            address += item + ' '
        print 'Restaurant Address: ' + address
        print 'Image: ' + image
        result = {'name': name, 'address': address, 'image': image}
        print result
        print '\n'
        return result
    else:
        print 'No restaurants found for %s' % location
        return 'No restaurants found'


if __name__ == '__main__':
    findARestaurant("Pizza", "Bilbao, Spain")
    findARestaurant("Pizza", "Tokyo, Japan")
    findARestaurant("Tacos", "Jakarta, Indonesia")
    findARestaurant("Tapas", "Maputo, Mozambique")
    findARestaurant("Falafel", "Cairo, Egypt")
    findARestaurant("Spaghetti", "New Delhi, India")
    findARestaurant("Cappuccino", "Geneva, Switzerland")
    findARestaurant("Sushi", "Los Angeles, California")
    findARestaurant("Steak", "La Paz, Bolivia")
    findARestaurant("Gyros", "Sydney Australia")
