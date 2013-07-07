import urllib2, re, HTMLParser
from BeautifulSoup import BeautifulSoup

class Oneworld:
    """ Interact with the oneworld interactive map web services.
        e.g., to download oneworld route lists.
    """

    def __init__(self, wsroot="http://mtk.innovataw3svc.com"):
        """ 
            wsroot -- The best URL for oneworld map web services.
        """
        self.wsroot = wsroot


    def get_all_data(self):
        """ Get all data available.
        """

        data = {"routes": {}}
        data['map'] = self.get_map_data()

        for city in data['map']['city']:
            city_code = city['citycode']
            data['routes'][city_code] = self.get_routes(city_code)

        return data


    def get_map_data(self, wspath="/MapDataToolKitServices.asmx"):
        """ Get the oneworld cities from the web server.

            wspath -- Path to the web services (optional)
        """

        payload = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <tns:GetMapData xmlns:tns="http://MapDataToolKitServices.com/">
      <tns:_sMapDataSearchXML>&lt;GetMapData_Input customerCode="ONW" customerSubCode="0" productCode="MAP6.0" lang="EN" mode="GEN"/&gt;</tns:_sMapDataSearchXML>
    </tns:GetMapData>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

        response = self.do_soap_request(wspath, "\"http://MapDataToolKitServices.com/GetMapData\"", payload)

        data_types = ['hub', 'link', 'carrier', 'equipment', 'city', 'country']
        out = {}
        for typ in data_types:
            values = self.parse_response_list(response, "GetMapDataResult", typ)
            out[typ] = values

        return out

            
    def do_soap_request(self, wspath, action, payload):
        """ Send a SOAP request to the server

            wspath -- The web service URL path
            action -- The SOAPAction header
            payload -- The SOAP request itself
        """

        url = "{0}{1}".format(self.wsroot, wspath)

        req = urllib2.Request(url, payload)
        req.add_header("Accept", "*/*")
        req.add_header("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.3")
        req.add_header("Content-Type", "text/xml; charset=utf-8")
        req.add_header("Referer", "http://onw.innosked.com/map/FlightMaps_v6.swf/[[DYNAMIC]]/2")
        req.add_header("Origin", "http://onw.innosked.com")
        req.add_header("SOAPAction", action)
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17")
        response = urllib2.urlopen(req)
        return response.read()


    def get_routes(self, city_code, wspath="/MapDataToolKitServices.asmx"):
        """ Request a list of destinations from a departure city.

            city_code -- Departure city code, three-letter city code (e.g., LON for London, EDI for Edinburgh).
            wspath -- The URL path for this web service.
        """

        payload = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <tns:GetDirectRouteList xmlns:tns="http://MapDataToolKitServices.com/">
      <tns:_sDirectRouteSearchXML>&lt;GetDirectRouteList_Input customerCode="ONW" customerSubCode="0" productCode="MAP6.0" lang="EN" mode="GEN" dptCode="{0}" dptCodeType="CTY" arvCodeType="ALL"/&gt;</tns:_sDirectRouteSearchXML>
    </tns:GetDirectRouteList>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
""".format(city_code)

        response = self.do_soap_request(wspath, "\"http://MapDataToolKitServices.com/GetDirectRouteList\"", payload)

        routes = self.parse_response_list(response, "GetDirectRouteListResult", "route")
        return routes


    def get_uniq_routes(self, city_code):
        """ Request a list of destinations from a departure city.

            city_code -- Departure city code, three-letter city code (e.g., LON for London, EDI for Ediburgh).
        """

        routes = self.get_routes(city_code)
        uniq_routes = self.unique_routes(routes)
        return uniq_routes
        

    def format_routes(self, routes):
        """ Format a list of routes for human viewing.
        """
        formatted = ""
        for dptcode in routes:
            formatted += "{0}-\n".format(dptcode)
            for arvcode in routes[dptcode]:
                formatted += "..{0}\n".format(arvcode)
            formatted += "\n"
        return formatted


    def unique_routes(self, routes):
        """ Return all unique routes from a list of routes.
        """
        uniq_routes = {}

        for route in routes:
            dptcode = route['dptcode']
            if dptcode not in uniq_routes:
                uniq_routes[dptcode] = []
            arvcode = route['arvcode']
            if arvcode not in uniq_routes[dptcode]:
                uniq_routes[dptcode].append(arvcode)

        return uniq_routes


    def parse_response_list(self, response, tag, innerTag):
        """ Parse a reponse list from the map web service.

            response -- SOAP response XML string.
            tag -- The tag to return the contents of.
            innerTag -- The inner tag of each item.
        """

        route_list_enc = self.parse_soap(response, tag)
        h = HTMLParser.HTMLParser()
        route_list = h.unescape(route_list_enc)

        route_soup = BeautifulSoup(route_list) 
        routes = []
        for route in route_soup.findAll(innerTag):
            route_dict = dict(route.attrs)
            routes.append(route_dict)

        return routes


    def parse_soap(self, response, tag):
        """ Parse a SOAP response, and return the content of the specified inner tag.

            response -- SOAP response XML string.
            tag -- The inner tag to return the contents of.
        """

        exp = "<{0}>(.*?)</{0}>".format(tag)
        matches = re.search(exp, response)
        return matches.group(1)

