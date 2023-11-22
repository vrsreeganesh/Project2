import googlemaps
import folium
from datetime import datetime
import polyline

def get_google_maps_client(api_key):
    return googlemaps.Client(key=api_key)

def get_location_coordinates(gmaps, address):
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print(f"Error: Unable to retrieve coordinates for {address}.")
        return None, None

def get_popular_places(gmaps, location, radius=1000, types=None):
    places_result = gmaps.places_nearby(
        location=location,
        radius=radius,
        type=types
    )

    popular_places = []
    for place in places_result['results']:
        popular_places.append({
            'name': place['name'],
            'location': place['geometry']['location'],
        })

    return popular_places

def generate_walk_route(api_key, current_location, duration_minutes):
    gmaps = get_google_maps_client(api_key)

    # Get coordinates for the current location
    start_location = get_location_coordinates(gmaps, current_location)

    if not start_location:
        print("Error: Unable to get coordinates for the current location.")
        return

    # Get popular places nearby
    popular_places = get_popular_places(gmaps, start_location, radius=1000, types='point_of_interest')

    # Create a folium map and add the starting location
    folium_map = folium.Map(location=start_location, zoom_start=15)

    # Add a marker for the starting location
    folium.Marker(
        location=[start_location[0], start_location[1]],
        popup="Start Location",
        icon=folium.Icon(color='blue')
    ).add_to(folium_map)

    # Generate walking route passing through popular places
    route_coordinates = []
    remaining_duration = duration_minutes * 60  # Convert duration to seconds
    current_location = start_location

    for place in popular_places:
        # Get walking directions to the popular place
        directions_result = gmaps.directions(
            current_location,
            place['location'],
            mode="walking",
            departure_time=datetime.now()
        )

        # Extract the polyline from the directions result
        polyline_points = directions_result[0]['overview_polyline']['points']
        route_segment_coordinates = polyline.decode(polyline_points)
        route_coordinates.extend(route_segment_coordinates)

        # Update the current location
        current_location = place['location']

        # Deduct the travel time from the remaining duration
        remaining_duration -= directions_result[0]['legs'][0]['duration']['value']

        # Break if the remaining duration is not enough for the next place
        if remaining_duration <= 0:
            break

    # Add the final step to return to the starting location
    directions_result = gmaps.directions(
        current_location,
        start_location,
        mode="walking",
        departure_time=datetime.now()
    )
    polyline_points = directions_result[0]['overview_polyline']['points']
    route_segment_coordinates = polyline.decode(polyline_points)
    route_coordinates.extend(route_segment_coordinates)

    # Add the walking route to the folium map
    folium.PolyLine(route_coordinates, color="green", weight=5, opacity=0.7).add_to(folium_map)

    # Add markers for popular places
    for place in popular_places:
        folium.Marker(
            location=[place['location']['lat'], place['location']['lng']],
            popup=place['name'],
            icon=folium.Icon(color='red')
        ).add_to(folium_map)

    # Save the folium map to an HTML file and open it in a web browser
    folium_map.save("walking_path_map.html")
    print("Walking path map generated and saved as 'walking_path_map.html'. Open the file in a web browser.")

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual Google Maps API key
    api_key = 'USE_YourAPI'

    # Input the current location and desired duration in minutes
    current_location = input("Enter your current location: ")
    duration_minutes = int(input("Enter the desired walk duration in minutes: "))

    generate_walk_route(api_key, current_location, duration_minutes)

