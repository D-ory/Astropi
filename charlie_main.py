import astro_pi_orbit
import math
import time
import csv
from skyfield.api import load, EarthSatellite, Loader
import numpy as np
from picamzero import Camera

# How long the program will run for in seconds
RUN_TIME = 545
# The time between measurements / speed calculations
INTERVAL = 1
camera = Camera()

# Get a list of the most populous cities of the world from a csv file from World Cities Database on simplemaps.com (creative commons licence)
rows = []
get_nearest_city = True
try:
    with open("worldcities.csv") as file:
        csvreader = csv.reader(file)
        fields = next(csvreader)
        for row in csvreader:
            # Add every city with a population above 50_000 to the list
            if row[9] and float(row[9]) > 50000: 
                rows.append([row[1], float(row[2]), float(row[3])])
except:
    print("Failed to open worldcities.csv file!")
    get_nearest_city = False

# Initialise the module to get ISS coordinates
iss = astro_pi_orbit.ISS()
point = iss.coordinates()
prev_height = point.elevation.km
prev_lat = point.latitude.radians
prev_long = point.longitude.radians

# Gets the time after 1st reading
process_end_time = time.time()

# Get the curved distance between two points on a sphere (the earth) using the Haversine formula
def haversine(coord1, coord2, radius):
    a = (math.sin((coord2[0] - coord1[0]) / 2))**2 + math.cos(coord1[0]) * math.cos(coord2[0]) * (math.sin((coord2[1] - coord1[1]) / 2)**2)
    distance = 2 * radius * math.asin(math.sqrt(a))
    return distance

# Get the radius at a specific latitude
def get_radius(latitude):
    a = 6378.137
    b = 6356.7523412
    deglat = math.degrees(latitude)
    radius = math.sqrt((((a**2)*math.cos(latitude))**2 + ((b**2)*(math.sin(latitude)))**2) / ((a*math.cos(latitude))**2 + (b * math.sin(latitude))**2))
    return radius

# Find the nearest city to the given coordinates
def nearest_city(coord, radius):
    if get_nearest_city == False:
        return "feature_disabled"
    dist = None
    best_row = ""
    for row in rows:
        new_dist = haversine(coord, (math.radians(row[1]), math.radians(row[2])), radius)
        if dist == None or new_dist < dist:
            dist = new_dist
            best_row = row
    return best_row[0]

def main():
    global prev_height, prev_lat, prev_long
    start_time = time.time()

    output_file = None
    try:
        # Output file contains our final speed estimate
        output_file = open("result.txt", "w")
    except:
        print("Output file could not be created! Aborting")
        return

    # Data file is a csv file containing all data we collected for later analysis
    data_file = None
    try:
        data_file = open("data.csv", "w")
        data_file.write('"time","latitude","longitude","radius","speed","nearest_city"\n')
    except:
        print("Data file could not be created or written to!")

    # This is the sum of all the calculated speeds so we can calculate a mean at the end
    total = 0
    # This is the number of speeds we calculated so we can calculate a mean
    count = 0

    # Keep the loop running once every second until RUN_TIME ends
    while time.time() < start_time + RUN_TIME:
        # Set the start time to the time since the end of the last iteration
        process_start_time = process_end_time

        time.sleep(INTERVAL)

        # Take a photo every 60 seconds
        try:
            if count % 60 == 0:
                camera.take_photo(f'image{count // 60}.jpg')
        except:
            print("Could not take photo!")

        point = iss.coordinates()
        curr_height = point.elevation.km
        curr_lat = point.latitude.radians
        curr_long = point.longitude.radians

        # Set the end time
        process_end_time = time.time()

        # Calculate the mean radius of the earth between the two points
        radius = get_radius((prev_lat + curr_lat) / 2) + ((prev_height + curr_height) / 2)

        # Calculate our speed using the haversine formula
        distance_travelled = haversine((prev_lat, prev_long), (curr_lat, curr_long), radius)
        time_taken = process_end_time - process_start_time
        speed = distance_travelled / time_taken

        # Calculate the nearest city to the ISS
        city = nearest_city((curr_lat, curr_long), radius)

        # Add to our mean calculation variables
        total += speed
        count += 1

        # Update position and height data
        prev_height = curr_height
        prev_lat = curr_lat
        prev_long = curr_long

        # save data to a file in format time,lat,long,radius,speed,nearest_city
        csv_string = f'{(process_start_time - start_time):.1f},{math.degrees(prev_lat)},{math.degrees(prev_long)},{radius},{speed},"{city}"\n'
        if data_file != None:
            try:
                data_file.write(csv_string)
            except:
                print("Data file is not writable!")

    output_file.write(f"{total/count:.4f}")
    output_file.close()
    if data_file != None:
        data_file.close()

    print(f"Final Speed Estimate: {total / count: .4f}km/s")

if __name__ == "__main__":
   main()
