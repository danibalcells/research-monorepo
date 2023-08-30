import os
import math
import random

import googlemaps

GOOGLEMAPS_TOKEN = os.environ.get('GOOGLEMAPS_TOKEN')
gmaps = googlemaps.Client(key=GOOGLEMAPS_TOKEN)


def snap_to_road(lat, lng):
    snapped_points = gmaps.snap_to_roads((lat, lng))

    if snapped_points:
        location = snapped_points[0]['location']
        return location['latitude'], location['longitude']
    return None, None


def get_map_link(lat, lng):
    return f"https://www.google.com/maps?q={lat},{lng}"


def generate_random_point(lat, lng, min_distance_meters, max_distance_meters):
    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)

    # Convert the distance to a fraction of the earth's radius
    earth_radius = 6371000  # Earth radius in meters

    # Generate a random distance between the minimum and maximum
    random_distance = random.uniform(min_distance_meters / earth_radius, max_distance_meters / earth_radius)

    # Generate a random bearing (direction) between 0 and 360 degrees
    random_bearing = random.uniform(0, 2 * math.pi)

    # Calculate the new latitude and longitude
    new_lat_rad = lat_rad + random_distance * math.cos(random_bearing)
    new_lng_rad = lng_rad + random_distance * math.sin(random_bearing) / math.cos(lat_rad)

    # Convert the new latitude and longitude from radians to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lng = math.degrees(new_lng_rad)

    return new_lat, new_lng

