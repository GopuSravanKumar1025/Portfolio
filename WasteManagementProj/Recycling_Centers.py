import requests
from geopy.geocoders import Nominatim
import ssl
import certifi

class Recycling_Centers:
    def Search_For_center(postcode, radius_miles=20):
        radius_meters = radius_miles * 1609.34
        geolocator = Nominatim(user_agent="geoapi")
        location = geolocator.geocode(postcode)
        if location:
            lat, lon = location.latitude, location.longitude
            url = f"https://overpass-api.de/api/interpreter?data=[out:json];node[amenity=recycling](around:{radius_meters},{lat},{lon});out;"
            response = requests.get(url, verify=certifi.where())
            if response.status_code == 200:
                data = response.json()
                recycling_centers = []
                for element in data.get('elements', []):
                    tags = element.get('tags', {})
                    name = tags.get('name')
                    if name != None and 'unknown':
                        latitude = element.get('lat')
                        longitude = element.get('lon')
                        recycling_centers.append({
                            "name": name,
                            "latitude": latitude,
                            "longitude": longitude
                            })
                return recycling_centers
            else:
                print("Failed to fetch recycling centers from OSM.")
                return []
        else:
            print("Invalid postcode.")
            return []
