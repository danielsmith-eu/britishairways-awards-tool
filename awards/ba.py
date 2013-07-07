import sys, re, json, mechanize, logging, time, pprint, datetime, uuid, os
from BeautifulSoup import BeautifulSoup

""" A class to search for British Airways/Oneworld award availability.
"""
class BA:
    debug_dir = u"debug"
    def __init__(self, debug=False, config=None):
        self.debug = debug
        self.config = config
        self.logged_in = False
        self.b = None

        # ensure mechanize debug logging is on
        if self.debug:
            loggers = ["mechanize", "mechanize.forms", "ROOT"]
            for loggername in loggers:
                logger = logging.getLogger(loggername)
                logger.addHandler(logging.StreamHandler(sys.stdout))
                logger.setLevel(logging.INFO)

    def write_html(self, html):
        """ Save HTML to the debug directory, ordered by time (UUID). """
        if self.debug:
            if not os.path.exists(self.debug_dir):
                os.mkdir(self.debug_dir)
            f = open(self.debug_dir + os.sep + unicode(uuid.uuid1()) + u".html", "w")
            f.write(html)
            f.close

    def load_config(self, config_filename):
        """ Load the configuration from a JSON file. """

        # load configuration
        config_file = open(config_filename, "r")
        self.config = json.load(config_file)
        config_file.close()
        # check for non-default values
        assert(self.config['ba']['username'] != "")
        assert(self.config['ba']['password'] != "")

    def lookup_dates(self, from_code, to_code, dates, travel_class, adults):
        """ Lookup award availability for a date range. """

        if self.config is None:
            raise Exception("Configuration not loaded.")

        if "-" in dates:
            # multiple dates
            (start_date, end_date) = dates.split("-")
        else:
            # single date
            start_date = dates
            end_date = dates

        if "," in to_code:
            # multiple destinations
            to_codes = to_code.split(",")
        else:
            to_codes = [to_code]

        # parse the strings to datetime.date objects
        start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")

        def daterange(start_date, end_date):
#            if start_date == end_date:
#                yield start_date
#            else:
            for n in range(int ((end_date - start_date).days + 1)):
                yield start_date + datetime.timedelta(n)

        results = {}
        for single_date in daterange(start_date, end_date):
            for current_to_code in to_codes:
                date = single_date.strftime("%d/%m/%Y") #, single_date.timetuple()) 
                print "Checking {0}, {1}-{2}".format(date, from_code, current_to_code)
                result = self.lookup_day(from_code, current_to_code, date, travel_class, adults)
                print "... {0} flights".format(sum(map(lambda x: len(x), result.values())))
                for day in result:
                    if day not in results:
                        results[day] = []
                    results[day].extend(result[day])

        return results


    def lookup_day(self, from_code, to_code, date, travel_class, adults):
        """ Lookup award availability for a single day. """

        if self.config is None:
            raise Exception("Configuration not loaded.")

        # re-use browser if one exists
        if self.logged_in:
            response = self.b.open(self.config['ba']['base'])
        else:
            # submit login form
            self.b = mechanize.Browser(factory=mechanize.RobustFactory())
            self.b.set_debug_http(self.debug)
            self.b.set_debug_redirects(self.debug)
            self.b.set_debug_responses(self.debug)
            self.b.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=2)

            self.b.open(self.config['ba']['base'])
            self.b.select_form(name="navLoginForm")
            self.b['membershipNumber'] = self.config['ba']['username']
            self.b['password'] = self.config['ba']['password']
            response = self.b.submit()

        # replace select input of classes with the real list (done with JS on the actual site)
        html = response.get_data()
        html = html.replace('<select id="cabin" name="CabinCode" class="withLink"><option>x</option></select>', '<select id="cabin" name="CabinCode" class="withLink"><option value="M">Economy</option><option value="W">Premium economy</option><option value="C">Business/Club</option><option value="F">First</option></select>')
        response.set_data(html)
        self.b.set_response(response)

        # submit initial award form
        self.b.select_form(name="plan_redeem_trip")
        self.b['departurePoint'] = from_code
        self.b['destinationPoint'] = to_code
        self.b['departInputDate'] = date
        self.b.find_control(name='oneWay').items[0].selected = True
        self.b['CabinCode'] = [travel_class]
        self.b['NumberOfAdults'] = [adults]
        response = self.b.submit()
        html = response.read()
        self.write_html(html)

        # go into loop of checking for interstitial pages / stopover pages
        while True:
            if 'name="pageid" value="STOPOVERROUTE"' in html:
                if self.debug:
                    print "Ignoring stopovers option."
                self.b.select_form("plan_trip")
                response = self.b.submit()
                html = response.read()
                self.write_html(html)
            elif 'name="pageid" value="REDEEMINTERSTITIAL"' in html:
                if self.debug:
                    print "At interstitial page, refreshing..."

                ### This stopped working early 2013.
                # extract the replacement URL from the javascript
                #replaceURL = ""
                #for url in re.findall(r'replaceURL[ +]= \'(.*?)\'', html):
                #    replaceURL += url

                # var eventId= '111011';
                eventId = re.search(r'var eventId=.*\'(.+)\'',html).group(1)
                logging.debug("eventID is: {0}".format(eventId))
                if eventId is None:
                    raise Exception("Cannot parse interstitial page. It is not possible to lookup this flight.")

                self.b.select_form(nr=1) # select the second form (SubmitFromInterstitial), the first is the nav.
                self.b.form.set_all_readonly(False) # otherwise we can't set eId below
                self.b.form['eId'] = eventId 

                time.sleep(0.5) # wait 500ms
                #response = self.b.open(replaceURL)
                response = self.b.submit()
                html = response.read()
                self.write_html(html)
            else:
                break
    
        if "We are unable to find seats for your journey" in html:
            if self.debug:
                print "No availability for date: {0}".format(date)
            return []
        else:
            if self.debug:
                print "We found availability for the date: {0}".format(date)

        results = {}
        results[date] = self.parse_flights(html)
        return results

    def parse_flights(self, html):
        """ Parse the BA HTML page into a structured dict of flight options. """
        if self.debug:
            out = open("results.html", "w")
            out.write(html)
            out.close()

        results = []

        # parse with BeautifulSoup
        soup = BeautifulSoup(html)
        for table in soup.findAll("table", {"class": "flightListTable"}):
            # ignore the outer tables
            if table.get("id") is not None:
                continue

            result = {}
            for tr in table.findAll("tr"):
                flight = {}
                for span in tr.findAll("span"):
                    cls = span.get("class")
                    if cls is None:
                        continue
                    if "departtime" in cls:
                        flight['departs'] = span.string
                    if "arrivaltime" in cls:
                        flight['arrives'] = span.string
                    if "journeyTime" in cls:
                        # journey time is total per result not per flight
                        result['duration'] = span.string.replace(u'\xa0', u' ')
                for a in tr.findAll("a"):
                    cls = a.get("class")
                    if cls is None:
                        continue
                    if "airportCodeLink" in cls:
                        if "route" not in flight:
                            flight['route'] = []
                        flight['route'].append(a.string)
                    if "flightPopUp" in cls:
                        flight['flight'] = a.string
                for td in tr.findAll("td"):
                    cls = td.get("class")
                    if cls is None:
                        continue
                    if "classoftravel" in cls:
                        if td.string == "" or td.string is None:
                            flight['class'] = td.a.string # BA flights have a link to the class
                        else:
                            flight['class'] = td.string # AA etc flights do not

                if flight != {}:
                    if "flights" not in result:
                        result['flights'] = []
                    result['flights'].append(flight)

            results.append(result)

        return results

    def format_results(self, results):
        """ Format a structured dict of flight optons (from parse_flights) into a human-readable list. """
        if self.debug:
            simple = pprint.pformat(results, indent=2)
            print simple

        lines = ""
        dates = sorted(results) # order the dates
        for date in dates:
            for result in results[date]:
                count = 0
                for flight in result['flights']:
                    if count == 0:
                        lines += date +"  "
                    else:
                        lines += "          .."

                    lines += flight['flight'] + " "
                    lines += "-".join(flight['route']) + " "
                    lines += flight['departs'] + "-" + flight['arrives'] + " "
                    lines += "(" + flight['class'] + ")"

                    count += 1

                    if count == len(result['flights']):
                        lines += ", " + result['duration']

                    lines +=  "\n" # flight newline
            lines += "\n" # date separator


        return lines

