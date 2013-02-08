import sys, traceback, argparse
from awards.ba import BA
from datasources.oneworld import Oneworld

parser = argparse.ArgumentParser(description='Look up oneworld award flight availability via British Airways.')
parser.add_argument('from', metavar='FROM', type=str, nargs=1,
                   help='Departure Airport (3-letter Code, e.g. LHR)')
parser.add_argument('--to', metavar='TO', type=str, nargs=1,
                   help='Arrival Airport (3-letter Code, e.g. LHR), leave blank to find all oneworld flights from the departure city')
parser.add_argument('dates', metavar='DATES', type=str, nargs=1,
                   help='Date or Date Range in DD/MM/YYYY or DD/MM/YYYY-DD/MM/YYYY format')
parser.add_argument('class', metavar='CLASS', type=str, nargs=1,
                   help='Class of travel as 1-letter code, where Economy=M, Premium Economy=W, Business=C and First=F')
parser.add_argument('adults', metavar='adults', type=str, nargs=1,
                   help='number of adults')

args = vars(parser.parse_args())

from_code = args['from'][0]
date = args['dates'][0]
travel_class = args['class'][0]
adults = args['adults'][0]

if args['to'] is None:
    # to_code is blank, so return a list of flights from the departure city
    ow = Oneworld()

    try:
        routes = ow.get_routes(from_code)
        formatted = ow.format_routes(routes)
        print formatted
    except Exception as e:
        print "There was an error running the search:\n"
        traceback.print_exc()

else:
    to_code = args['to'][0]
    # to_code is present, so search for award availability
    ba = BA(debug=False)

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

