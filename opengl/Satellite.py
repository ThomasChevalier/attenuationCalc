from utility import header_indexes
import math
import csv
import glm

class Satellite:
    def __init__(self, norad_id):
        self.states = {}          # Positions, line of sight, path loss, indexed by time
        self.norad_id = norad_id  # Norad ID

    def add_state(self, time, long, lat, altitude, los, path_loss):
        """add_position
        Args:
            time: the time at wich the satellite is in this position
            long: longitude in degrees
            lat: latitude in degrees
            altitude: altitude (from earth's surface) in meters
            los: wheter or not the satellite is in line of sight with our target (1 if True, 0 if False)
            path_loss: path loss in db between this satellite and our target
        """
        if time in self.states and self.states[time] != (long, lat, altitude, los, path_loss):
            raise RuntimeError("Two different states at the same time ({} s) specified for satellite {}".format(time, self.norad_id))
        self.states[time] = (long, lat, altitude, los, path_loss)

    def at(self, time):
        """Linear interpolation that gives the state of the satellite at any given time."""
        if time in self.states:
            return self.states[time]

        t1, t2 = None, None
        lastT = None
        # positions is sorted because it is a dict of floats
        for i, t in enumerate(self.states):
            if t > time:
                if lastT is None:
                    raise RuntimeError("Given time ({} s) is out of range for satellite {}".format(time, self.norad_id))
                t2, t1 = t, lastT
                break
            lastT = t
        if t1 is None:
            raise RuntimeError("Given time ({} s) is out of range for satellite {}".format(time, self.norad_id))

        state1, state2 = self.states[t1], self.states[t2]
        interp = []
        for a, b in zip(state1, state2):
            interp.append(a + (b-a)*(time-t1)/(t2-t1))
        return interp

    def posToScene(self, state, earth_x, earth_y, earth_z, earth_radius):
        long, lat, altitude = state[:3]
        u, v = math.radians(lat), math.radians(long)
        r = (1 + altitude/6.3781e6) * earth_radius
        y = r * math.sin(u) # z
        z = - r * math.cos(u) * math.cos(v)  # x
        x = - r * math.cos(u) * math.sin(v)  # y
        return glm.vec3(x+earth_x, y+earth_y, z+earth_z)


def load_from_file(file):
    """Load trajectories from given csv file and returns Satellite objects as satellites, relays;
    with relays a list of Satellite corresponding to the relays.
    Aditionnaly returns t_min and t_max"""
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        header = next(reader, None)
        relays_name = []
        relays_headers = []
        for column in header:
            if ":" in column and column.split(":")[0] not in relays_name:
                name = column.split(":")[0]
                relays_name.append(name)
                relays_headers.extend([name + s for s in [":longitude (°)", ":latitude (°)", ":altitude (m)", ":los", ":path_loss (dB)"]])
        indices = header_indexes(header, ["time (s)", "longitude (°)", "latitude (°)", "altitude (m)"] + relays_headers)

        satellite = Satellite("satellite")
        relays = [Satellite(name) for name in relays_name]
        times = []
        for row in reader:
            t = float(row[indices[0]])
            times.append(t)
            long, lat, altitude = float(row[indices[1]]), float(row[indices[2]]), float(row[indices[3]])
            satellite.add_state(t, long, lat, altitude, 0, 0)

            for i, relay in enumerate(relays):
                # Same order as requested headers
                long, lat, altitude, los, path_loss = float(row[indices[i*5+4]]), float(row[indices[i*5+5]]), float(row[indices[i*5+6]]), b2f(row[indices[i*5+7]]), e2f(row[indices[i*5+8]])
                relay.add_state(t, long, lat, altitude, los, path_loss)

    return satellite, relays, min(times), max(times)


def b2f(b):
    """bool to float"""
    return 1.0 if b == "True" else 0.0


def e2f(b):
    """empty to float"""
    return 0 if b == "" else float(b)
