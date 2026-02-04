import astro_pi_orbit
import math
import time
import csv
from skyfield.api import load, EarthSatellite, Loader
import numpy as np
from picamzero import Camera

RUN_TIME = 5
camera = Camera()
"""rows = []
with open("worldcities.csv") as file:
    csvreader = csv.reader(file)
    
    
    fields = next(csvreader)
    for row in csvreader:
        if row[9] and float(row[9]) > 50000: 
            rows.append([row[1], float(row[2]), float(row[3])])"""

iss = astro_pi_orbit.ISS()
point = iss.coordinates()
prev_height = point.elevation.km
prev_lat = point.latitude.radians
prev_long = point.longitude.radians
#rows.sort(key=lambda x:x[2])
#rows.sort(key=lambda x:x[1])

def haversine(coord1, coord2, radius):
    a = (math.sin((coord2[0] - coord1[0]) / 2))**2 + math.cos(coord1[0]) * math.cos(coord2[0]) * (math.sin((coord2[1] - coord1[1]) / 2)**2)
    distance = 2 * radius * math.asin(math.sqrt(a))
    return distance

def get_radius(latitude):
    a = 6378.137
    b = 6356.7523412
    deglat = math.degrees(latitude)
    radius = math.sqrt((((a**2)*math.cos(latitude))**2 + ((b**2)*(math.sin(latitude)))**2) / ((a*math.cos(latitude))**2 + (b * math.sin(latitude))**2))
    return radius

"""def nearest_city(coord, radius):
    dist = 9999999999
    best_row = ""
    for row in rows:
        new_dist = haversine(coord, (math.radians(row[1]), math.radians(row[2])), radius)
        if new_dist < dist:
            dist = new_dist
            best_row = row
    return best_row[0]"""

def main():
    global prev_height, prev_lat, prev_long
    start_time = time.time()
    f = open("result.txt", "w")
    total = 0
    count = 0
    t = time.time()
    while time.time() < start_time + RUN_TIME:
        time.sleep(1)
        if count % 60 == 0:
            camera.take_photo(f'image.jpg')

        point = iss.coordinates()
        curr_height = point.elevation.km
        curr_lat = point.latitude.radians
        curr_long = point.longitude.radians

        radius = get_radius((prev_lat + curr_lat) / 2) + ((prev_height + curr_height) / 2)
        speed = haversine((prev_lat, prev_long), (curr_lat, curr_long), radius)
        print(speed / (time.time() - t))
        total += speed / (time.time() - t)
        count += 1

        prev_height = curr_height
        prev_lat = curr_lat
        prev_long = curr_long
        t = time.time()
        #print(nearest_city((curr_lat, curr_long), radius))
    print(total / count)
    f.write(f"{total/count:.4f}")
    f.close()

if __name__ == "__main__":
   main() 
