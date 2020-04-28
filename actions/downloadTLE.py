from bs4 import BeautifulSoup
import concurrent.futures
import urllib.request
import os.path
import csv

from utility import confirmation, header_indexes


def downloadTLE(context):
    """
    Get the newest TLE from a satellite tracking website.
    TLE are accurate for 2 weeks after they are generated.

    Args:
        id_file: the file where the norad id are read.
        save_file: the file where to save the results.
        confirm: whether or not we have to ask for confirmation.
    """

    id_file = context.id_file
    confirm = context.confirm
    save_file = context.download_file

    satellites_data = []  # List of all the properties of a satellite in id_file
    satellites_id = []    # List of all the norad_id
    satellites_tle = {}   # Dict of index -> TLE, with index pointing elements of satellites_id (or satellite_data, same index)
    header = None

    print("Downloading TLE")

    # Get all the norad numbers
    with open(id_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader, None)

        norad_column = header_indexes(header, ["norad_id"])[0]

        for row in reader:
            satellites_data.append(row)
            satellites_id.append(row[norad_column])

    # Check if the output file already exists
    if confirm and os.path.isfile(save_file):
        if not confirmation("\"{}\" already exists. Overwrite it ?".format(save_file)):
            raise RuntimeError("Aborting download.")

    # Download all TLE
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_index = {executor.submit(getTLE, satellites_id[i]): i for i in range(len(satellites_id))}
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                tle = future.result()
            except Exception as exc:
                print("Satellite #{} generated an exception: {}".format(satellites_id[index], exc))
            else:
                satellites_tle[index] = tle

    # Write the result to the csv file
    with open(save_file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(header + ["tle1", "tle2"])
        for i in range(len(satellites_id)):
            if i in satellites_tle:
                spamwriter.writerow(satellites_data[i] + satellites_tle[i])
            else:
                print("Error: satellite #{} don't have any TLE".format(satellites_id[i]))


def getTLE(noradID):
    data = urllib.request.urlopen('https://www.n2yo.com/satellite/?s='+str(noradID)).read()
    soup = BeautifulSoup(data, features="html.parser")
    element = soup.find('div', attrs={'id': 'tle'})
    if element is None:
        return ""
    element = element.find('pre')
    if element is None:
        return ""
    TLE = element.text.strip().split('\n')
    return [s.strip() for s in TLE]
