import sys
import logging
import pprint
import datetime
import uuid
import os
import string
import requests
from BeautifulSoup import BeautifulSoup

""" A class to search for British Airways/Oneworld award availability.
"""
class BA2:
    
    debug_dir = u"debug"

    classAKA = {
        "economy": "economy",
        "business": "business",
        "premium": "premium",
        "first": "first",
        "M": "economy",
        "S": "economy",
        "N": "economy",
        "O": "economy",
        "B": "economy",
        "H": "economy",
        "Y": "economy",
        "W": "premium",
        "T": "premium",
        "E": "premium",
        "C": "business",
        "J": "business",
        "R": "business",
        "F": "first",
        "A": "first",
    }

    classesReal = {
        "economy": "Economy",
        "premium": "Premium Economy",
        "business": "Business Class",
        "first": "First Class",
        "0": "Unknown Class", # Our code used internally here
    }

    def __init__(self, debug=False, info=False):
        self.debug = debug
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
        self.cj.save()

    def lookup_one(self, src, dst, pax, cls, start, end):
        t = string.Template("http://www.baredemptionfinder.com/search?source=$src&destination=$dst&number_of_passengers=$pax&class=$cls")
        url = t.safe_substitute(src=src,dst=dst,pax=pax,cls=cls)
        self.logger.info("Getting URL: {0}".format(url))
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html)
        results = {}
        for div in soup.findAll("div", {"class": "outbound"}):
            self.logger.info("Outbound")
            for li in div.findAll("li"):
                self.logger.info("Li {0}".format(li.string))
                day, month, year = li.string.split(" ")[0].split("/")
                if (len(day) == 1):
                    day = "0" + day
                if (len(month) == 1):
                    month = "0" + month 
                if (len(year) == 2):    
                    year = "20" + year
                date = year + month + day
                if (int(date) >= int(start) and int(date) <= int(end)):
                    nicedate = year + "/" + month + "/" + day
                    if (nicedate not in results.keys()):
                        results[nicedate] = []
                    results[nicedate].append({"route": [src, dst], "class": self.classesReal[cls]})
        return results

    def lookup_dates(self, from_code, to_code, dates, travel_class, adults, directonly):
        """ Lookup award availability for a date range. """

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

        # parse the strings to YYYYMMDD
        start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y%m%d")

        results = {}
        sofar = 0
        for current_from_code in from_codes:
            for current_to_code in to_codes:
                for current_travel_class in travel_classes:
                    code = self.classAKA[current_travel_class]
                    self.logger.info("Checking {0}-{1}, {2} ({3} seats)".format(current_from_code, current_to_code, code, adults))
                    result = self.lookup_one(current_from_code, current_to_code, adults, code, start_date, end_date)
                    count = len(result)
                    sofar += count
                    self.logger.info("... {0} flights ({1} total)".format(count, sofar))
                    if count > 0:
                        self.notify("Found {0} flight(s) {1}-{2}".format(count,current_from_code,current_to_code))
                    for day in result.keys():
                        if day not in results:
                            results[day] = []
                        results[day].extend(result[day])
        return results


    def format_results(self, results):
        """ Format a structured dict of flight optons (from parse_flights) into a human-readable list. """
        if self.debug:
            self.logger.debug("Formatting these results: ")
            simple = pprint.pformat(results, indent=2)
            self.logger.debug(simple)

        lines = ""
        dates = sorted(results) # order the dates
        for date in dates:
            for result in results[date]:
                lines += date +"  "
                lines += "-".join(result['route']) + " "
                lines += "(" + result['class'] + ")"
                lines +=  "\n" # flight newline
        return lines

