import sys, traceback
from awards.ba import BA

# TODO replace with command line options
from_code = "LHR"
to_code = "JFK"
#date = "01/02/2013" # can be a single date e.g. 01/02/2013 or a range e.g. 01/02/2013-02/02/2013
date = "01/02/2013-05/02/2013" # can be a single date e.g. 01/02/2013 or a range e.g. 01/02/2013-02/02/2013
# Economy = M, Premium Economy = W, Business = C, First = F
travel_class = "M"
adults = "1"

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

