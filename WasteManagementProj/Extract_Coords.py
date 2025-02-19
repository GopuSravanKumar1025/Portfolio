import requests
import json

class ExtractCoordinates:
    @staticmethod
    def LocateCoords(postcode):
        Lat_LNG = []
        api_key = "YOUR API KEY"
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={postcode}&key={api_key}"
        response = requests.get(geocode_url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                location = data["results"][0]['geometry']['location']
                _Latitude = location['lat']
                _Longitude = location['lng']
                LatLong = {
                    '_Latitude' : _Latitude,
                    '_Longitude' : _Longitude
                }
                Lat_LNG.append(LatLong)
                return Lat_LNG
        return None