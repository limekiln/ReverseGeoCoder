import csv
import sys
import os
import logging
import time
import traceback

from pathlib import Path

from locationiq.geocoder import LocationIQ
from locationiq.geocoder import LocationIqInvalidKey, LocationIqNoPlacesFound, LocationIqRequestLimitExeceeded
from dotenv import load_dotenv

load_dotenv()
logging.getLogger().setLevel(logging.INFO)
SAVE_DIRECTORY = Path(sys.path[0]).joinpath(Path("Reports", "location_report.csv"))


def set_save_directory(directory):
    global SAVE_DIRECTORY
    SAVE_DIRECTORY = directory


def check_arguments(args):
    global SAVE_DIRECTORY
    if len(args) < 2:
        sys.exit('No argument was given, please provide a .csv file!')
    if len(args) < 3:
        logging.info(f"No target location for report creation selected. Using default: {SAVE_DIRECTORY}")
    else:
        target = Path(args[2])
        if not target.suffix == ".csv":
            sys.exit("Invalid path for report creation. Target has to be a .csv file!")
        else:
            logging.info(f"Report location set to {SAVE_DIRECTORY}.")
            set_save_directory(target)

    file = Path(args[1])
    if not file.is_file() or not file.suffix == '.csv':
        sys.exit('No valid .csv file found!')


def init_report_file():
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
    locations = []
    try:
        sleepTimer = int(os.environ["SLEEP_TIMER"])
    except KeyError:
        sleepTimer = 0
        logging.info("No value for sleep timer found, setting to 1 ...")

    # iterate through csv file and do reverse geo coding calls
    with open(source, newline='') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=' ', quotechar='|')
        next(csvReader, None)  # ignore the header
        logging.info("Starting address calculation ...")
        for row in csvReader:
            time.sleep(sleepTimer)
            try:
                location = geoCoder.reverse_geocode(*row)['address']
                location.update(latitude=row[0], longitude=row[1])
                locations.append(location)
            except LocationIqInvalidKey:
                sys.exit("The given API key is invalid!")
            except LocationIqNoPlacesFound:
                logging.warning(f"No place found for {row[0]} {row[1]}. Skipping...")
                continue
            except LocationIqRequestLimitExeceeded:
                logging.warning("Request limit exceeded. Skipping all remaining coordinates ...")
                break
            except KeyError:
                logging.warning(f"No postal code found for {row[0]} {row[1]}. Skipping...")
                continue
            except Exception as e:
                logging.error(
                    f"An unexpected error occurred during reverse geo coding: ${traceback.print_tb(e.__traceback__)}")

    return locations


def write_results(locations):
    logging.info("Writing locations to report file ...")
    keys = set().union(*(location.keys() for location in locations))  # get all keys from dicts
    with open(SAVE_DIRECTORY, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(locations)
    logging.info(f"... done! Report located at {SAVE_DIRECTORY}.")


if __name__ == '__main__':
    logging.info("Start reverse geo coding...")

    # validation check for command line arguments
    check_arguments(sys.argv)

    inputFile = sys.argv[1]

    # create file and write header
    init_report_file()

    # initialize geo coder with API key -> does not throw on invalid key, but on a missing one
    geoCoder = get_locationiq_geo_coder()

    # array to contain valid locations
    validLocations = execute_reverse_geo_coding(inputFile, geoCoder)

    # Write results to report at SAVE_DIRECTORY
    write_results(validLocations)

    logging.info("Execution finished!")
