from Index import Data
from validatepostcode import validate_postcode
from Recycling_Centers import Recycling_Centers
from LocatePostCode import Post_Code_locate
from Extract_Coords import ExtractCoordinates
from maps import maps_
from LocateMiles import miles
Data.Index()

postcode = input("Enter Address: ")
if len(postcode.split(',')) >= 2:
    validpostcode = validate_postcode.is_valid(postcode)
    print(validpostcode)
    Recycle_Centers = Recycling_Centers.Search_For_center(postcode)

    options = []
    for i, center in  enumerate(Recycle_Centers, 1):
        name = center.get('name', 'N/A')
        latitude = center.get('latitude', 'N/A')
        longitude = center.get('longitude', 'N/A')
        ExtractPostCode = Post_Code_locate.locate_postcode(latitude, longitude)
        Extract_miles = miles.LocateMiles(postcode, ExtractPostCode)
        Distance_rounded = round(Extract_miles, 1)
        Recycle_Data = f"{i}: {name}, {ExtractPostCode}, {Distance_rounded} mi"
        options.append({'name': name,'postcode': ExtractPostCode,'distance': Distance_rounded})
        sorted_options = sorted(options, key=lambda x: x['distance'])
    for i, option in enumerate(sorted_options, 1):
        print(f"{i}: {option['name']}, {option['postcode']}, {option['distance']} mi")
    select = int(input("select options from above: "))
    if 1 <= select <= len(sorted_options):
        selected_Data = sorted_options[select - 1]
        Start_Postcode = ExtractCoordinates.LocateCoords(postcode)
        End_Postcode = ExtractCoordinates.LocateCoords(selected_Data['postcode'])
        coords = {
            "Start_Coords" : f'{Start_Postcode[0]["_Latitude"]}, {Start_Postcode[0]["_Longitude"]}',
            "End_Coords" : f'{End_Postcode[0]["_Latitude"]}, {End_Postcode[0]["_Longitude"]}'
        }
        try:
            output = maps_.LocateMaps(coords, postcode, selected_Data)
            print(f'starting map to {selected_Data['name']}, {selected_Data['postcode']}, {selected_Data['distance']}')
        except Exception as e:
            print("No Data Found", e)

    else:
        print("Invalid selection")
else:
    print("please enter street address along with postcode")