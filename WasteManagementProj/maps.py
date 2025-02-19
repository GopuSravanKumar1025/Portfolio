import folium
import requests
import webbrowser
import polyline
from geopy.distance import geodesic

class maps_:
    @staticmethod
    def LocateMaps(coords, Starting_Address, Ending_Address, fileName = "Maps.html"):
        popup_text = f"{Ending_Address['name']}, {Ending_Address['postcode']}"
        start_coords = coords["Start_Coords"]
        end_coords = coords["End_Coords"]
        api_key = "YOUR API KEY"
        def get_route(start, end, api_key, waypoints=None):
            points = f"point={start}"
            if waypoints:
                for waypoint in waypoints:
                    points += f"&point={waypoint}"
            points += f"&point={end}"
            url = f"https://graphhopper.com/api/1/route?{points}&vehicle=car&key={api_key}&type=json&points_encoded=true"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'paths' in data and len(data['paths']) > 0:
                    return data['paths'][0]['points']
            return None
        def calculate_time(coords):
            distance = sum(geodesic(coords[i], coords[i+1]).kilometers for i in range(len(coords)-1))
            average_speed = 60
            time_hours = distance / average_speed
            time_minutes = (time_hours - int(time_hours)) * 60
            return int(time_hours), int(time_minutes)
        start_lat, start_lon = map(float, start_coords.split(","))
        end_lat, end_lon = map(float, end_coords.split(","))
        midpoint_lat = (start_lat + end_lat) / 2
        midpoint_lon = (start_lon + end_lon) / 2
        midpoint_coords = f"{midpoint_lat},{midpoint_lon}"
        low_traffic_lat = start_lat + (end_lat - start_lat) / 3
        low_traffic_lon = start_lon + (end_lon - start_lon) / 3
        low_traffic_waypoint = f"{low_traffic_lat},{low_traffic_lon}"
        high_traffic_route = get_route(start_coords, end_coords, api_key, waypoints=[midpoint_coords])
        low_traffic_route = get_route(start_coords, end_coords, api_key, waypoints=[low_traffic_waypoint])
        no_traffic_route = get_route(start_coords, end_coords, api_key)
        high_traffic_coords = polyline.decode(high_traffic_route) if high_traffic_route else []
        low_traffic_coords = polyline.decode(low_traffic_route) if low_traffic_route else []
        no_traffic_coords = polyline.decode(no_traffic_route) if no_traffic_route else []
        high_traffic_time = calculate_time(high_traffic_coords) if high_traffic_coords else (None, None)
        low_traffic_time = calculate_time(low_traffic_coords) if low_traffic_coords else (None, None)
        no_traffic_time = calculate_time(no_traffic_coords) if no_traffic_coords else (None, None)
        map_obj = folium.Map(location=[float(coord) for coord in start_coords.split(",")], zoom_start=12)
        if high_traffic_coords:
            time_str = f"{high_traffic_time[0]} hours, {high_traffic_time[1]} minutes"
            popup_content = f"High Traffic\nEstimated Time: {time_str}"
            folium.PolyLine(high_traffic_coords, color='red', weight=5, opacity=0.7, popup=popup_content).add_to(map_obj)
        if low_traffic_coords:
            time_str = f"{low_traffic_time[0]} hours, {low_traffic_time[1]} minutes"
            popup_content = f"Low Traffic\nEstimated Time: {time_str}"
            folium.PolyLine(low_traffic_coords, color='orange', weight=5, opacity=0.7, popup=popup_content).add_to(map_obj)
        if no_traffic_coords:
            time_str = f"{no_traffic_time[0]} hours, {no_traffic_time[1]} minutes"
            popup_content = f"No Traffic\nEstimated Time: {time_str}"
            folium.PolyLine(no_traffic_coords, color='blue', weight=5, opacity=0.7, popup=popup_content).add_to(map_obj)
        folium.Marker(location=[float(coord) for coord in start_coords.split(",")], popup=f'{Starting_Address}', icon=folium.Icon(color='green')).add_to(map_obj)
        folium.Marker(location=[float(coord) for coord in end_coords.split(",")], popup=popup_text, icon=folium.Icon(color='red')).add_to(map_obj)
        map_obj.save(fileName)
        webbrowser.open(fileName)