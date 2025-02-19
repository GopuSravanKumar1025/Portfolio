import openrouteservice
from geopy.geocoders import Nominatim
import re

class miles:
    def LocateMiles(Postcode1, Postcode2):
        postcode_pattern = r"[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}"
        match = re.search(postcode_pattern, Postcode1, re.IGNORECASE)
        if match:
            postcode = match.group()
            api_key = 'YOUR API KEY'
            geolocator = Nominatim(user_agent="postcode_locator")
            location_for_PC1 = geolocator.geocode(postcode)
            location_for_PC2 = geolocator.geocode(Postcode2)
            coords_1 = (location_for_PC1.latitude, location_for_PC1.longitude)
            coords_2 = (location_for_PC2.latitude, location_for_PC2.longitude)
            client = openrouteservice.Client(key=api_key)
            coordinates = [(coords_1[1], coords_1[0]), (coords_2[1], coords_2[0])]
            route = client.directions(coordinates, profile='driving-car', format='geojson')
            route_length = route['features'][0]['properties']['segments'][0]['distance']
            route_length_miles = route_length * 0.000621371
            return route_length_miles
        else:
            print("No postcode found.")