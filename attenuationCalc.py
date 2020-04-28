#!/usr/bin/python

import sys
import getopt
import time
import datetime

import actions


class Context:
    def __init__(self):
        # Files
        self.id_file = None
        self.download_file = ".tle_sat"
        self.tle_file = ".tle_sat"
        self.output_file = "output.csv"
        self.trajectory_file = None
        self.visualization_file = None

        self.confirm = True
        self.write_trajectories = False
        self.time = time.time()
        self.frequency = 1616e6


def get_time(string, opt):
    try:
        timestamp = float(string)
    except ValueError:
        print("{} argument must be a real number.".format(opt))
        return 0, False
    else:
        try:
            time = datetime.datetime.utcfromtimestamp(timestamp)
        except ValueError:
            print("Time {} is invalid, might be too big.".format(timestamp))
            return 0, False
        except OverflowError:
            print("Time {} is invalid, might be too big.".format(timestamp))
            return 0, False
        print("Time set to {} (UTC)".format(time))
        return timestamp, True


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "d:i:o:t:f:ha:v:", [
            "download=",
            "tle=",
            "noconfirm",
            "output=",
            "write-trajectories",
            "time=",
            "frequency=",
            "help",
            "trajectory=",
            "view="
        ])

    except getopt.GetoptError as E:
        print("ERROR: {}\n".format(E))
        usage()
        sys.exit(2)

    if len(args) != 0:
        print("Too many arguments.")
        sys.exit(1)

    # List of all the actions needed
    acts = []

    context = Context()

    for opt, arg in opts:
        if opt in ("-d", "--download"):
            acts.append(actions.Action("Download TLE coordinates", 0, actions.downloadTLE))
            context.id_file = arg

        elif opt in ("-i", "--tle"):
            context.tle_file = arg

        elif opt in ("--noconfirm"):
            context.confirm = False

        elif opt in ("-t", "--time"):
            context.time, valid = get_time(arg, opt)
            if not valid:
                sys.exit(1)

        elif opt in ("-o", "--output"):
            context.output_file = arg

        elif opt == "--write-trajectories":
            context.write_trajectories = True

        elif opt in ("-f", "--frequency"):
            try:
                context.frequency = float(arg)
            except ValueError:
                print("{} argument must be a real number.".format(opt))
                sys.exit(1)
            print(f"Frequency set to {context.frequency/1e6} MHz")

        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)

        elif opt in ("-a", "--trajectory"):
            acts.append(actions.Action("Calculate the trajectory", 10, actions.trajectory))
            context.trajectory_file = arg

        elif opt in ("--view"):
            acts.append(actions.Action("3D visualization of previous results.", 15, actions.view3D))
            context.visualization_file = arg

    # Sort actions according to their priority
    acts.sort(key=lambda a: a.priority)
    for action in acts:
        try:
            action.run(context)
        except RuntimeError as E:
            print("Error: {}".format(E))
            sys.exit(1)


def usage():
    ctx = Context()
    helpMessage = f"""
attenuationCalc - Thomas Chevalier
thomasom.chevalier@gmail.com

USAGE:
    python attenuationCalc.py [OPTIONS] MODE

OPTIONS:
    -d, --download <CSV FILE>:
        Download the TLE coordinates of the satellites listed in the CSV file. A header with the column "norad_id" must be present.
        Write the result in the file {ctx.download_file}.

    -i, --tle <CSV FILE>:
        Use the satellites mentionned in the file. The file must contains a header with the columns "norad_id", "tle1" and "tle2".
        By default the file {ctx.tle_file} is used.

    --noconfirm:
        Don't ask for confirmation.

    -o, --output <FILE NAME>:
        Specify the output file name.
        By default the file {ctx.output_file} is used.

    --write-trajectories:
        Write trajectories in the output file.
        By default the option is set to {ctx.write_trajectories}.

    -t, --time <TIME>:
        Set the time at wich the calculations start.
        <TIME> is the number of second since 01/01/1970 in UTC time.
        By default the current time (e.g. {ctx.time}) is used.

    -f, --frequency <FREQUENCY>:
        Set the frequency used to calculate path loss, in MHz.
        Default is {ctx.frequency/1e6} MHz.


    -h, --help:
        Show this help.

MODES:
    -a, --trajectory <TRAJECTORY FILE>:
        Calculate the attenuation of the signal in function of time, given a particular trajectory.
        The trajectory file must be in CSV format, with a header containing the following columns : altitude, longitude, latitude and time.

    -v, --view <TRAJECTORY FILE>:
        Three-dimensional visualization of the given file. Note: the file must have been generated with option --write-trajectories.

EXAMPLES:
    python ./attenuationCalc.py -d ./iridium_id.csv -o output_test.csv --write-trajectories -a ./serenade_ecc_0.csv --noconfirm
        Download tle data for satellites specified in iridium_id.csv (-d), calculate the path loss for the trajectory in serenade_ecc_0.csv (-a)
        output the result in output_win.csv (-o) and include trajectories data (--write-trajectories). Don't confirm before overwriting files (--noconfirm).

    python ./attenuationCalc.py --view ./output_test.csv
        Visualize data contained in output.csv.

    python ./attenuationCalc.py --write-trajectories -a ./serenade_ecc_0.csv --noconfirm --view output.csv
        Do the two commands above in one command.
        Here we take advantage of the default filename for the output file ("output.csv") and we don't download the TLE data because we assume they are
        already been downloaded.

"""
    print(helpMessage[1:-2])


if __name__ == '__main__':
    main(sys.argv[1:])
