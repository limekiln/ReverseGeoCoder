# LocationIQ Reverse GeoCoder

## What is it?
This script uses the locationIQ API to extract address information from a pair of
latitude and longitude coordinates and saves it as a .csv report.

## Configuration
There is a minimal configuration to be done using the .env file.
- `LOCATIONIQ_API_KEY`: Key used for geo-queries 
- `OVERRIDE`: Whether or not an existing report file should be overwritten (default: true)
- `SLEEP_TIMER`: Back-off-timer after a failed query to prevent too many queries in a too short time frame 
- `DELIMITER_IN`: Delimiter used in input .csv file
- `DELIMITER_OUT`: Delimiter which should be used for writing the report .csv file

## Usage
### CLI
`python GeoCoder.py <input.csv> [output.csv]`

### Executable
`path/to/GeoCoder <input.csv> [output.csv]`

### Docker
`docker container run --env-file .env 
-v GeoCoder:/Reports -v </path/to/input.csv:/input.csv> 
reverse_geo_coder <input.csv>`
