import astro_pi_orbit
import math
import time

from skyfield.api import load, EarthSatellite, Loader
import numpy as np

iss = astro_pi_orbit.ISS()
point = iss.coordinates()
prev_height = point.elevation.km
prev_lat = point.latitude.radians
prev_long = point.longitude.radians

def haversine(coord1, coord2, radius):
    a = (math.sin((coord2[0] - coord1[0]) / 2))**2 + math.cos(coord1[0]) * math.cos(coord2[0]) * (math.sin((coord2[1] - coord1[1]) / 2)**2)
    distance = 2 * radius * math.asin(math.sqrt(a))
    return distance

def get_radius(latitude):
    a = 6378.137
    b = 6356.7523412
    deglat = math.degrees(latitude)
    radius = math.sqrt((((a**2)*math.cos(latitude))**2 + ((b**2)*(math.sin(latitude)))**2) / ((a*math.cos(latitude))**2 + (b * math.sin(latitude))**2))
    print(radius)
    return radius


start_time = time.time()
while time.time() < start_time + 5:
    time.sleep(1)

    point = iss.coordinates()
    curr_height = point.elevation.km
    curr_lat = point.latitude.radians
    curr_long = point.longitude.radians

    radius = get_radius((prev_lat + curr_lat) / 2) + ((prev_height + curr_height) / 2)
    speed = haversine((prev_lat, prev_long), (curr_lat, curr_long), radius)
    print(speed)

    prev_height = curr_height
    prev_lat = curr_lat
    prev_long = curr_long
