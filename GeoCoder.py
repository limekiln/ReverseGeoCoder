import csv
import sys
import os

from pathlib import Path

from locationiq.geocoder import LocationIQ
from locationiq.geocoder import LocationIqInvalidKey, LocationIqNoPlacesFound, LocationIqRequestLimitExeceeded

SAVE_DIRECTORY = Path(sys.path[0]).joinpath(Path("location_report.csv"))


def set_save_directory(directory):
    global SAVE_DIRECTORY
    SAVE_DIRECTORY = directory


def check_arguments(args):
    global SAVE_DIRECTORY
    if len(args) < 2:
        sys.exit('No argument was given, please provide a .csv file!')
    if len(args) < 3:
        print(f"No target location for report creation selected. Using default: {SAVE_DIRECTORY}")
    else:
        target = Path(args[2])
        if not target.suffix == ".csv":
            sys.exit("Invalid path for report creation. Target has to be a .csv file!")
        else:
            print(f"Report location set to {SAVE_DIRECTORY}.")
            set_save_directory(target)

    file = Path(args[1])
    if not file.is_file() or not file.suffix == '.csv':
        sys.exit('No valid .csv file found!')


def init_report_file(report):
    # delete file if existing and environment variable OVERRIDE is set to true
    if os.getenv('OVERRIDE') == 'true' and SAVE_DIRECTORY.is_file():
        os.remove(SAVE_DIRECTORY)

    with open(SAVE_DIRECTORY, 'a', newline='') as reportFile:
        csvWriter = csv.writer(reportFile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(["Latitude", "Longitude", "Postal_Code"])


def get_locationiq_geo_coder():
    try:
        apiKey = os.environ['LOCATIONIQ_API_KEY']
        return LocationIQ(apiKey)
    except KeyError:
        sys.exit('Could not find API key in environment variables!')


def execute_reverse_geo_coding(source, geoCoder):
    validLocations = []
    # iterate through csv file and do reverse geo coding calls
    with open(source, newline='') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=' ', quotechar='|')
        next(csvReader, None)  # ignore the header
        for row in csvReader:
            try:
                location = geoCoder.reverse_geocode(*row)
                postalCode = location['address']['postcode']
                validLocations.append((row[0], row[1], postalCode))
                print(f"Found postal code {postalCode} for {row[0]} {row[1]}")
            except LocationIqInvalidKey:
                sys.exit("The given API key is invalid!")
            except LocationIqNoPlacesFound:
                print(f"No places found for {row[0]} {row[1]}. Skipping...")
                continue
            except LocationIqRequestLimitExeceeded:
                print("Request limit exceeded. Skipping ...")
                continue
            except KeyError:
                print(f"No postal code found for {row[0]} {row[1]}. Skipping...")
                continue

    return validLocations


def write_results():
    print("Writing locations to report file ...")
    try:
        for location in validLocations:
            with open(SAVE_DIRECTORY, 'a', newline='') as reportFile:
                csvWriter = csv.writer(reportFile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csvWriter.writerow(location)
    except Exception as e:
        print(e)
        return
    print(f"... done! Report located at {SAVE_DIRECTORY}.")


if __name__ == '__main__':
    # validation check for command line arguments
    check_arguments(sys.argv)

    inputFile = sys.argv[1]

    # create file and write header
    init_report_file(inputFile)

    # initialize geo coder with API key -> does not throw on invalid key, but on a missing one
    geoCoder = get_locationiq_geo_coder()

    # array to contain valid locations (independent of postal code existence)
    validLocations = execute_reverse_geo_coding(inputFile, geoCoder)

    # Write results to report at SAVE_DIRECTORY
    write_results()
