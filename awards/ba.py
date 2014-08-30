import sys
import re
import json
import mechanize
import logging
import time
import pprint
import datetime
import uuid
import os
from BeautifulSoup import BeautifulSoup
from exception import LoginException, CaptchaException

""" A class to search for British Airways/Oneworld award availability.
"""
class BA:
    
    debug_dir = u"debug"

    classes = {
        "M": "Economy",
        "W": "Premium Economy",
        "C": "Business Class",
        "F": "First Class",
        "0": "Unknown Class", # Our code used internally here
    }

    def __init__(self, debug=False, config=None, info=False):
        self.debug = debug
        self.config = config
        self.logged_in = False
        self.b = None
        self.logger = logging.getLogger("ba")

        # ensure mechanize debug logging is on
        if self.debug:
            loggers = ["mechanize", "mechanize.forms", "ROOT"]
            for loggername in loggers:
                logger = logging.getLogger(loggername)
                logger.addHandler(logging.StreamHandler(sys.stdout))
                logger.setLevel(logging.DEBUG)

        if info:
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
            self.logger.setLevel(logging.INFO)
        elif debug:
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
            self.logger.setLevel(logging.DEBUG)

    def notify(self, notify):
        try:
            from pync import Notifier
            Notifier.notify(notify, title="Award Availability Finder")
        except Exception as e:
            pass

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

    def lookup_dates(self, from_code, to_code, dates, travel_class, adults, directonly):
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

        # multiple departure airports
        from_codes = from_code.split(",")

        # multiple destinations
        to_codes = to_code.split(",")

        # multiple classes
        travel_classes = travel_class.split(",")

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
        sofar = 0
        for single_date in daterange(start_date, end_date):
            for current_from_code in from_codes:
                for current_to_code in to_codes:
                    for current_travel_class in travel_classes:
                        date = single_date.strftime("%d/%m/%Y") #, single_date.timetuple()) 
                        self.logger.info("Checking {0}, {1}-{2}, {3} ({4} seats)".format(date, current_from_code, current_to_code, self.classes[current_travel_class], adults))
                        result = self.lookup_day(current_from_code, current_to_code, date, current_travel_class, adults, directonly)
                        count = sum(map(lambda x: len(x), result.values()))
                        sofar += count
                        self.logger.info("... {0} flights ({1} total)".format(count, sofar))
                        if count > 0:
                            self.notify("Found {0} flight(s) {1}-{2} on {3}".format(count,current_from_code,current_to_code,date))
                        for day in result:
                            if day not in results:
                                results[day] = []
                            results[day].extend(result[day])

        return results

    def login(self):
        # re-use browser if one exists
        if not self.logged_in:
            # submit login form
            self.b = mechanize.Browser(factory=mechanize.RobustFactory())
            self.b.set_debug_http(self.debug)
            self.b.set_debug_redirects(self.debug)
            self.b.set_debug_responses(self.debug)
            self.b.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=2)

            self.b.open(self.config['ba']['base'])
            self.b.select_form(name="toploginform")
            self.b['membershipNumber'] = self.config['ba']['username']
            self.b['password'] = self.config['ba']['password']
            response = self.b.submit()
            html = response.get_data()

            if "We are not able to recognise the membership number or PIN/password that you have supplied" in html or "You have made too many invalid login attempts" in html:
                raise LoginException()

            # it worked
            self.logged_in = True

        # always re-get this page, after a successful login we are sent to the exec club homepage
        response = self.b.open(self.config['ba']['base'])
        return response

    def lookup_day(self, from_code, to_code, date, travel_class, adults, directonly):
        """ Lookup award availability for a single day. """

        if self.config is None:
            raise Exception("Configuration not loaded.")

        response = self.login()
        html = response.get_data()

        self.write_html(html)
        # replace select input of classes with the real list (done with JS on the actual site)
        html = html.replace('<select name="CabinCode" class="m" id="cabin"><option>x</option></select>', '<select id="cabin" name="CabinCode" class="withLink"><option value="M">Economy</option><option value="W">Premium economy</option><option value="C">Business/Club</option><option value="F">First</option></select>')
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
                    self.logger.debug("Ignoring stopovers option.")
                self.b.select_form("plan_trip")
                response = self.b.submit()
                html = response.read()
                self.write_html(html)
            elif 'name="pageid" value="REDEEMINTERSTITIAL"' in html:
                if self.debug:
                    self.logger.debug("At interstitial page, refreshing...")

                ### This stopped working early 2013.
                # extract the replacement URL from the javascript
                #replaceURL = ""
                #for url in re.findall(r'replaceURL[ +]= \'(.*?)\'', html):
                #    replaceURL += url

                # var eventId= '111011';
                eventId = re.search(r'var eventId = \'(.+)\'',html).group(1)
                self.logger.debug("eventID is: {0}".format(eventId))
                if eventId is None:
                    raise Exception("Cannot parse interstitial page. It is not possible to lookup this flight.")

                self.b.select_form(nr=1) # select the second form (SubmitFromInterstitial), the first is the nav.
                self.b.form.set_all_readonly(False) # otherwise we can't set eId below
                self.b.form['eId'] = eventId 

                time.sleep(0.1) # wait 500ms
                #response = self.b.open(replaceURL)
                response = self.b.submit()
                html = response.read()
                self.write_html(html)
            else:
                break
    
        if "We are unable to find seats for your journey" in html or "Sorry, there are no flights available on " in html:
            if self.debug:
                self.logger.debug("No availability for date: {0}".format(date))
            return {date: []}
        elif "we need to check you are a real person" in html:
            raise CaptchaException()
        else:
            if self.debug:
                self.logger.debug("We found availability for the date: {0}".format(date))

        results = {}
        results[date] = self.parse_flights(html, directonly)
        return results

    def parse_flights(self, html, directonly):
        """ Parse the BA HTML page into a structured dict of flight options. """
        if self.debug:
            out = open("results.html", "w")
            out.write(html)
            out.close()

        results = []

        # parse with BeautifulSoup
        soup = BeautifulSoup(html)
        #for table in soup.findAll("table[class=tblLyOut]"):
        route = []
        for table in soup.findAll("table"):
            cls = table.get("class")
            if cls is None:
                continue

            if not("flightListTable" in cls):
                continue

            # ignore the outer tables
            if table.get("id") is not None:
                continue

            # get the header in case the route is listed in it (does this for some direct routes)
            if len(route) == 0:
                for thead in table.findAll("thead"):
                    for a in thead.findAll("a", {"class": "airportCodeLink"}):
                        if len(route) < 2:
                            route.append(a.string)

            result = {}

            for tbody in table.findAll("tbody"):
                for tr in tbody.findAll("tr"):
                    if tr.get("id") and tr.get("id")[0:4] == "smry":
                        continue # this is a summary row, hidden to users that contains > 1 flight information, we ignore it

                    flight = {}
                    cabincode = "0"
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
                        if "flightPopUp" in cls:
                            flight['flight'] = a.string

                        # these are if the route is in the first column in side the cell with the time and date
                        # sometimes they are in the column headers, see below
                        if "airportCodeLink" in cls:
                            if "route" not in flight:
                                flight['route'] = []

                            if len(flight['route']) < 2: # it will repeat after 2 because the page repeats them
                                flight['route'].append(a.string)

                        # capturing the route 

                    for inpu in tr.findAll("input", {"type": "radio"}):
                        cabincode = "0"
                        codes = {"CabinCodeF": "F", "CabinCodeC": "C", "CabinCodeW": "W", "CabinCodeM": "M"}
                        for code_find, code in codes.items():
                            if code_find in inpu.get("id"):
                                cabincode = code
                                continue

                        if 'class' in flight and flight['class'] != '': # since each query returns more than one class now
                            flight['class'] += "/"
                        else:
                            flight['class'] = ""
                        flight['class'] += self.classes[cabincode]

    #                for td in tr.findAll("td"):
    #                    cls = td.get("class")
    #                    if cls is None:
    #                        continue
    #                    if "classoftravel" in cls:
    #                        if td.string == "" or td.string is None:
    #                            flight['class'] = td.a.string # BA flights have a link to the class
    #                        else:
    #                            flight['class'] = td.string # AA etc flights do not

                    if flight != {}:
                        if "flights" not in result:
                            result['flights'] = []

                        # add the route from the header column if it wasn't included in the individual rows
                        if flight.get("route") is None:
                            flight['route'] = route

                        if flight.get("class") is None:
                            flight['class'] = self.classes[cabincode]

                        result['flights'].append(flight)

                if result != {}: # some rows have no flights / data at all now
                    if directonly and len(result['flights']) > 1:
                        self.logger.info("Skipping non-direct flight with {0} segments.".format(len(result['flights'])))
                    else:
                        results.append(result)

        return results

    def format_results(self, results):
        """ Format a structured dict of flight optons (from parse_flights) into a human-readable list. """
        if self.debug:
            self.logger.debug("Formatting these results: ")
            simple = pprint.pformat(results, indent=2)
            self.logger.debug(simple)

        count = None
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

        if count is None or count == 0:
            return ""

        return lines

