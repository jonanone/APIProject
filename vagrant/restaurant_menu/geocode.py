import httplib2
import json

from secret_keys import GOOGLE_API_KEY


def getGeocodeLocation(inputString):
    google_api_key = GOOGLE_API_KEY
    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/' +
           'json?address=%s&key=%s' % (
                locationString,
                google_api_key)
           )
    h = httplib2.Http()
    response, content = h.request(url, 'GET')

    result = json.loads(content)
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return (latitude, longitude)
