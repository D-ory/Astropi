from astro_pi_orbit import ISS
import math as m
import time

iss = ISS()
point = iss.coordinates()
prev_height = point.elevation.km
prev_lat = point.latitude.radians
prev_long = point.longitude.radians
def haversine(x1, x2):
    return m.sin((x1 - x2) / 2) ** 2

def Haversine_formula(radius, coord1, coord2):
    angle = m.asin((haversine(coord1[0], coord2[0]) + m.cos(coord1[0]) * m.cos(coord2[0]) * haversine(coord1[1], coord2[1]) ** 0.5))
    return 2 * radius * angle


while True:
    time.sleep(1)
    
    point = iss.coordinates()
    curr_height = point.elevation.km
    curr_lat = point.latitude.radians
    curr_long = point.longitude.radians
    print(Haversine_formula(6370 + ((prev_height + curr_height) / 2), (prev_lat, prev_long), (curr_lat, curr_long)))
    
    prev_height = curr_height
    prev_lat = curr_lat
    prev_long = curr_long
    print(prev_lat * (180 / m.pi))