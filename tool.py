import sys
import traceback
import argparse
import logging
from awards.ba import BA
from awards.exception import LoginException
from datasources.oneworld import Oneworld
#from datasources.alldata import AllData

parser = argparse.ArgumentParser(description='Look up oneworld award flight availability via British Airways.')
parser.add_argument('from', type=str, action="store", help='Departure Airport (3-letter Code, e.g. LHR)')
parser.add_argument('--to', type=str, action="store",
                   help='Arrival Airport (3-letter Code, e.g. LHR), leave blank to find all oneworld flights from the departure city. Comma separate multiple airportsm e.g. EDI,MAN,DUB,NCL')
parser.add_argument('dates', type=str, action="store",
                   help='Date or Date Range in DD/MM/YYYY or DD/MM/YYYY-DD/MM/YYYY format')
parser.add_argument('class', type=str, action="store",
                   help='Class of travel as 1-letter code, where Economy=M, Premium Economy=W, Business=C and First=F')
parser.add_argument('adults', type=str, action="store", help='Number of adults')
parser.add_argument('--debug', default=False, action="store_true", help='Enable very verbose logging')
parser.add_argument('--info', default=False, action="store_true", help='Enable information logging while searching')
parser.add_argument('--directonly', default=False, action="store_true", help='Only return direct flights')

args = vars(parser.parse_args())

# download data sources
#ad = AllData()
#data = ad.get_data()

if args['to'] is None:
    # Destination airport is blank, so return a list of flights from the departure city
    ow = Oneworld()

    try:
        routes = ow.get_uniq_routes(args['from'])
        formatted = ow.format_routes(routes)
        print formatted
    except Exception as e:
        logging.error("There was an error running the search:".format(traceback.format_exc()))

else:
    # Destination airport is present, so search for award availability
    ba = BA(debug=args['debug'], info=args['info'])

    try:
        ba.load_config("config.json")
    except Exception as e:
        # error if the file isn't present or if default values are still present
        logging.error("Configuration could not be loaded, ensure that config.json.default has been copied to config.json, and that empty values have been filled in.")
        sys.exit(1)

    try:
        results = ba.lookup_dates(args['from'], args['to'], args['dates'], args['class'], args['adults'], args['directonly'])
        formatted = ba.format_results(results)
        if len(formatted) > 0:
            print formatted
    except LoginException as e:
        logging.error("PIN/Username and/or password are incorrect, fix them in config.json.");
    except Exception as e:
        logging.error("There was an error running the search: {0}".format(traceback.format_exc()))

