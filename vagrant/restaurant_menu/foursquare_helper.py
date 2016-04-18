import httplib2
import json

from secret_keys import FOURSQUARE_CLIENT_ID
from secret_keys import FOURSQUARE_CLIENT_SECRET


def getCategoryId(categoryName):
    url = ('https://api.foursquare.com/v2/venues/categories?' +
           'client_id=%s&client_secret=%s&v=20130815' %
           (FOURSQUARE_CLIENT_ID,
            FOURSQUARE_CLIENT_SECRET))
    h = httplib2.Http()
    response, content = h.request(url, 'GET')

    result = json.loads(content)
    categories = result['response']['categories']
    print categories
    for category in categories:
        lowerName = category['name'].lower()
        if categoryName.lower() in lowerName:
            return category['id']
        else:
            subcategories = category['categories']
            if subcategories:
                for subcategory in subcategories:
                    lowerName = subcategory['name'].lower()
                    if categoryName.lower() in lowerName:
                        return subcategory['id']
    return 0


def findNearbyRestaurantsByMealType(latitude,
                                    longitude,
                                    mealType):
    geoLocation = str(latitude) + ',' + str(longitude)
    radius = "10000"
    categoryId = getCategoryId('Food')
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&'
           'client_secret=%s&v=20130815&ll=%s&query=%s&intent=browse&'
           'radius=%s&categoryId=%s' %
           (FOURSQUARE_CLIENT_ID,
            FOURSQUARE_CLIENT_SECRET,
            geoLocation,
            mealType,
            radius,
            categoryId)
           )
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    result = json.loads(content)
    return result


def findNearbyVenueByMealType(latitude,
                              longitude,
                              mealType):
    geoLocation = str(latitude) + ',' + str(longitude)
    radius = "10000"
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&'
           'client_secret=%s&v=20130815&ll=%s&query=%s&intent=browse&'
           'radius=%s' %
           (FOURSQUARE_CLIENT_ID,
            FOURSQUARE_CLIENT_SECRET,
            geoLocation,
            mealType,
            radius)
           )
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    result = json.loads(content)
    return result


def getVenuePhotos(venueId):
    url = ('https://api.foursquare.com/v2/venues/%s/photos?'
           'v=20130815&client_id=%s&client_secret=%s' %
           (venueId, FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET))
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    result = json.loads(content)
    return result
