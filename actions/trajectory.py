from skyfield.api import Loader, EarthSatellite, Topos
from skyfield.functions import length_of
import datetime
import os.path
import math
import csv

import numpy as np

from utility import confirmation, header_indexes


def path_loss(frequency, dist):
    """Returns the path loss (in dB) given a frequency and a distance."""

    return 20*math.log10(4*math.pi*dist*frequency/299792458)


def los_to_earth(position, pointing):
    """Find if the line defined by the pointing vector intersects with the Earth.
    https://medium.com/@stephenhartzell/satellite-line-of-sight-intersection-with-earth-d786b4a6a9b6

    Finds the intersection of a pointing vector u and starting point s with the WGS-84 geoid
    Args:
        position : length 3 array defining the starting point location(s) in meters
        pointing : length 3 array defining the pointing vector(s) (must be a unit vector)
    Returns:
        bool: wheter or not the ray (position, pointing) intersects the Earth
    """

    a = 6371008.7714
    b = 6371008.7714
    c = 6356752.314245
    x = position[0]
    y = position[1]
    z = position[2]
    u = pointing[0]
    v = pointing[1]
    w = pointing[2]

    value = -a**2*b**2*w*z - a**2*c**2*v*y - b**2*c**2*u*x
    radical = a**2*b**2*w**2 + a**2*c**2*v**2 - a**2*v**2*z**2 + 2*a**2*v*w*y*z - a**2*w**2*y**2 + b**2*c**2*u**2 - b**2*u**2*z**2 + 2*b**2*u*w*x*z - b**2*w**2*x**2 - c**2*u**2*y**2 + 2*c**2*u*v*x*y - c**2*v**2*x**2
    magnitude = a**2*b**2*w**2 + a**2*c**2*v**2 + b**2*c**2*u**2

    if radical < 0:
        return False
    d = (value - a*b*c*np.sqrt(radical)) / magnitude
    return d > 0


def line_of_sight(pos_sat, pos_relay):
    """Return wheter or not the two satellites are in light of sight.

    This assumes that the satellites is always closer to the Earth than the relay.
    See https://medium.com/@stephenhartzell/satellite-line-of-sight-intersection-with-earth-d786b4a6a9b6.

    Args:
        pos_sat: a skyfield Geocentric object
        pos_relay: a skyfield Geocentric object
    """
    sat_pos = np.array(pos_sat.itrf_xyz().m)
    relay_pos = np.array(pos_relay.itrf_xyz().m)

    pointing = relay_pos - sat_pos
    norm = np.linalg.norm(pointing)
    pointing = pointing / norm
    return not los_to_earth(sat_pos, pointing)


def trajectory(context):
    """Calculate the path loss for a given trajectory.

    Args (context):
        tle_file: the file containing the TLE of all the satellites, must contains the following columns: tle1, tle2, norad_id.
        trajectory_file: the file containing the trajectory, must contains the following columns: altitude, longitude, latitude, time.
        frequency: the frequency, in hertz, of the carrier
        timestamp: the UTC Epoch timestamp (number of seconds since 01/01/1970).
        output_file: the file where the data are saved.
        confirm: whether or not we have to ask for confirmation.
    """

    satellites_file    = context.tle_file
    trajectory_file    = context.trajectory_file
    frequency          = context.frequency
    timestamp          = context.time
    save_file          = context.output_file
    write_trajectories = context.write_trajectories
    confirm            = context.confirm

    print("Calculating the trajectory")

    # Set up skyfield
    load = Loader(".")
    data = load('de421.bsp')
    ts   = load.timescale()
    planets = load('de421.bsp')

    # Load satellites orbits
    satellites = {}
    with open(satellites_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        header = next(reader, None)
        tle1_index, tle2_index, id_index = header_indexes(header, ["tle1", "tle2", "norad_id"])
        for row in reader:
            name, L1, L2 = row[id_index], row[tle1_index], row[tle2_index]
            satellites[name] = EarthSatellite(L1, L2)

    # Check if the output file already exists
    if confirm and os.path.isfile(save_file):
        if not confirmation("\"{}\" already exists. Overwrite it ?".format(save_file)):
            raise RuntimeError("Aborting trajectory calculation.")

    # Calculate attenuation at each point of the trajectory
    data = []  # List of list, [time, dist1, dist2, ..., dist N, minimum dist, minimum name, path_loss]

    with open(trajectory_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader, None)
        altitude_index, longitude_index, latitude_index, time_index = header_indexes(header, ["altitude", "longitude", "latitude", "time"])

        for row in reader:
            try:
                altitude, longitude, latitude, rela_time = float(row[altitude_index]), float(row[longitude_index]), float(row[latitude_index]), float(row[time_index])
            except ValueError:
                raise RuntimeError("Ill-formed trajectory file.")
            epoch_time = timestamp + rela_time
            new_time = datetime.datetime.utcfromtimestamp(epoch_time)
            time = ts.utc(new_time.year, new_time.month, new_time.day, new_time.hour, new_time.minute, new_time.second)
            pos = Topos(longitude_degrees=longitude, latitude_degrees=latitude, elevation_m=altitude).at(time)

            data.append([epoch_time, longitude, latitude, altitude])

            min_dist = math.inf
            min_name = "None"
            dists = []
            for name, sat in satellites.items():
                pos_relay = sat.at(time)
                dist = length_of((pos_relay-pos).distance().m)
                dists.append(dist)
                los = line_of_sight(pos, pos_relay)
                dists.append(path_loss(frequency, dist) if los else "")
                dists.append(line_of_sight(pos, pos_relay))
                if los and dist < min_dist:
                    min_dist = dist
                    min_name = name

                if write_trajectories:
                    sub = pos_relay.subpoint()
                    # dists.extend(list(pos_relay.itrf_xyz().m))
                    dists.extend([sub.longitude.degrees, sub.latitude.degrees, sub.elevation.m])

            data[-1].append(min_dist)
            data[-1].append(min_name)
            data[-1].append(path_loss(frequency, min_dist))
            data[-1].extend(dists)

    # Save the file
    with open(save_file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        sat_headers = []
        for name in satellites:
            sat_headers.extend([name + ":dist (m)", name + ":path_loss (dB)", name + ":los"])
            if write_trajectories:
                sat_headers.extend([name+":longitude (°)", name+":latitude (°)", name+":altitude (m)"])
        spamwriter.writerow(["time (s)", "longitude (°)", "latitude (°)", "altitude (m)"] + ["minimum_dist (m)", "minimum_name (norad id)", "path_loss (dB)"] + sat_headers)
        for line in data:
            spamwriter.writerow(line)
