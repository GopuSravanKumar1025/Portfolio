from opencage.geocoder import OpenCageGeocode


class Post_Code_locate:
    @staticmethod
    def locate_postcode(latitude, longitude):
        api_key = 'YOUR_APIKEY'
        geocoder = OpenCageGeocode(api_key)
        result = geocoder.reverse_geocode(latitude, longitude)
        if result and len(result):
            postal_code = result[0]['components'].get('postcode', 'Postal code not found')
            return postal_code
        else:
            print('Postal code not found')

