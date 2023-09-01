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


def calculate_bearing(start_lat, start_lng, end_lat, end_lng):
    """
    Calculate the bearing between two points.
    The formula used to calculate the bearing between two points is:
        θ = atan2(sin(Δlong).cos(lat2), cos(lat1).sin(lat2) - sin(lat1).cos(lat2).cos(Δlong))
    :param start_lat: Starting latitude
    :param start_lng: Starting longitude
    :param end_lat: Ending latitude
    :param end_lng: Ending longitude
    :returns: initial bearing in degrees
    """
    start_lat = math.radians(start_lat)
    start_lng = math.radians(start_lng)
    end_lat = math.radians(end_lat)
    end_lng = math.radians(end_lng)

    d_lng = end_lng - start_lng
    y = math.sin(d_lng) * math.cos(end_lat)
    x = math.cos(start_lat) * math.sin(end_lat) - math.sin(start_lat) * math.cos(end_lat) * math.cos(d_lng)
    initial_bearing = math.atan2(y, x)

    # Convert bearing from radians to degrees
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def generate_random_point(lat, lng, min_distance_meters, max_distance_meters, blocked_point=None):
    earth_radius = 6371000  # Earth radius in meters

    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)

    # Calculate the bearing to the blocked point, if provided
    if blocked_point:
        blocked_bearing = calculate_bearing(lat, lng, blocked_point[0], blocked_point[1])

    while True:
        random_distance = random.uniform(min_distance_meters / earth_radius, max_distance_meters / earth_radius)
        random_bearing = random.uniform(0, 2 * math.pi)

        new_lat_rad = lat_rad + random_distance * math.cos(random_bearing)
        new_lng_rad = lng_rad + random_distance * math.sin(random_bearing) / math.cos(lat_rad)

        new_lat = math.degrees(new_lat_rad)
        new_lng = math.degrees(new_lng_rad)

        if blocked_point:
            if (blocked_bearing - 45 <= random_bearing * (180/math.pi) <= blocked_bearing + 45):
                continue

        return new_lat, new_lng
