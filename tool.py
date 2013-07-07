import sys, traceback, argparse
from awards.ba import BA
from datasources.oneworld import Oneworld
from datasources.alldata import AllData

parser = argparse.ArgumentParser(description='Look up oneworld award flight availability via British Airways.')
parser.add_argument('from', type=str, action="store", help='Departure Airport (3-letter Code, e.g. LHR)')
parser.add_argument('--to', type=str, action="store",
                   help='Arrival Airport (3-letter Code, e.g. LHR), leave blank to find all oneworld flights from the departure city. Comma separate multiple airportsm e.g. EDI,MAN,DUB,NCL')
parser.add_argument('dates', type=str, action="store",
                   help='Date or Date Range in DD/MM/YYYY or DD/MM/YYYY-DD/MM/YYYY format')
parser.add_argument('class', type=str, action="store",
                   help='Class of travel as 1-letter code, where Economy=M, Premium Economy=W, Business=C and First=F')
parser.add_argument('adults', type=str, action="store", help='Number of adults')
parser.add_argument('--debug', default=False, action="store_true", help='Enable verbose logging')

args = vars(parser.parse_args())

from_code = args['from']
date = args['dates']
travel_class = args['class']
adults = args['adults']

debug = args['debug']

# download data sources
#ad = AllData()
#data = ad.get_data()

if args['to'] is None:
    # to_code is blank, so return a list of flights from the departure city
    ow = Oneworld()

    try:
        routes = ow.get_uniq_routes(from_code)
        formatted = ow.format_routes(routes)
        print formatted
    except Exception as e:
        print "There was an error running the search:\n"
        traceback.print_exc()

else:
    to_code = args['to']
    # to_code is present, so search for award availability
    ba = BA(debug=debug)

    try:
        ba.load_config("config.json")
    except Exception as e:
        # error if the file isn't present or if default values are still present
        print "Configuration could not be loaded, ensure that config.json.default has been copied to config.json, and that empty values have been filled in.\n"
        sys.exit(1)

    try:
        results = ba.lookup_dates(from_code, to_code, date, travel_class, adults)
        formatted = ba.format_results(results)
        print formatted
    except Exception as e:
        print "There was an error running the search:\n"
        traceback.print_exc()

