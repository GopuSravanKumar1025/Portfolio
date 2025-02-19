import requests
import json
import re


class validate_postcode:
    def is_valid(address):
        postcode_pattern = r"[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}"
        match = re.search(postcode_pattern, address, re.IGNORECASE)
        if match:
            postcode = match.group()
            api_key = 'YOUR API KEY'
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    for component in data['results'][0]['address_components']:
                        if 'postal_code' in component['types']:
                            if component['long_name'] == postcode:
                                return f'{postcode} is verified'
                            else:
                                return f'{postcode} is not a valid postcode. please enter correct postcode'
                else:
                    return f'{postcode} is not a valid postcode. please enter correct postcode'
            else:
                return response.text
        else:
            return "Please Enter Valid PostCode"
