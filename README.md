britishairways-awards-tool
==========================

A tool for searching British Airways/Avios awards more easily

Usage:

    Look up oneworld award flight availability via British Airways.

    positional arguments:
      from        Departure Airport (3-letter Code, e.g. LHR)
      dates       Date or Date Range in DD/MM/YYYY or DD/MM/YYYY-DD/MM/YYYY format
      class       Class of travel as 1-letter code, where Economy=M, Premium
                  Economy=W, Business=C and First=F
      adults      Number of adults

    optional arguments:
      -h, --help  show this help message and exit
      --to TO     Arrival Airport (3-letter Code, e.g. LHR), leave blank to find
                  all oneworld flights from the departure city. Comma separate
                  multiple airportsm e.g. EDI,MAN,DUB,NCL
      --debug     Enable verbose logging




Example of a North American flight:

    $ python tool.py JFK --to MIA 10/03/2013 F 1
    Checking 10/03/2013
    10/03/2013  AA1141 JFK-MIA 05:40-08:50 (First), 03 hours 10 minutes
    10/03/2013  AA0443 JFK-MIA 07:15-10:45 (First), 03 hours 30 minutes
    10/03/2013  AA0647 JFK-MIA 09:00-12:20 (First), 03 hours 20 minutes
    10/03/2013  AA2041 JFK-MIA 12:40-15:55 (First), 03 hours 15 minutes
    10/03/2013  AA1769 JFK-MIA 14:55-18:25 (First), 03 hours 30 minutes
    10/03/2013  AA0543 JFK-MIA 17:29-20:49 (First), 03 hours 20 minutes


Example of a Europe to Asia flight:

    $ python tool.py LHR --to HKG 10/03/2013-11/03/2013 C 1
    Checking 10/03/2013
    Checking 11/03/2013
    10/03/2013  CX0256 LHR-HKG 20:40-16:30 (Business), 11 hours 50 minutes
    10/03/2013  BA0017 LHR-ICN 13:00-08:55 (Club World)
              ..CX0417 ICN-HKG 10:20-13:15 (Business), 16 hours 15 minutes

    11/03/2013  CX0256 LHR-HKG 20:40-16:30 (Business), 11 hours 50 minutes
    11/03/2013  BA0017 LHR-ICN 13:00-08:55 (Club World)
              ..CX0417 ICN-HKG 10:20-13:15 (Business), 16 hours 15 minutes

Example showing flights to multiple destinations:

    $ python tool.py LON --to EDI,MAN,DUB,NCL 10/11/2013 C 1
    Checking 10/11/2013, LON-EDI
    ... 13 flights
    Checking 10/11/2013, LON-MAN
    ... 7 flights
    Checking 10/11/2013, LON-DUB
    ... 1 flights
    Checking 10/11/2013, LON-NCL
    ... 6 flights
    10/11/2013  BA1434 LHR-EDI 08:00-09:20 (Domestic), 01 hours 20 minutes
    10/11/2013  BA1442 LHR-EDI 08:55-10:20 (Domestic), 01 hours 25 minutes
    10/11/2013  BA2938 LGW-EDI 10:55-12:20 (Domestic), 01 hours 25 minutes
    10/11/2013  BA1440 LHR-EDI 11:45-13:10 (Domestic), 01 hours 25 minutes
    10/11/2013  BA1446 LHR-EDI 15:20-16:40 (Domestic), 01 hours 20 minutes
    10/11/2013  BA1452 LHR-EDI 16:20-17:45 (Domestic), 01 hours 25 minutes
    10/11/2013  BA1454 LHR-EDI 17:25-18:50 (Domestic), 01 hours 25 minutes
    10/11/2013  BA2942 LGW-EDI 17:45-19:10 (Domestic), 01 hours 25 minutes
    10/11/2013  BA1458 LHR-EDI 18:35-20:00 (Domestic), 01 hours 25 minutes
    10/11/2013  BA8708 LCY-EDI 19:05-20:20 (Domestic), 01 hours 15 minutes
    10/11/2013  BA2946 LGW-EDI 19:55-21:20 (Domestic), 01 hours 25 minutes
    10/11/2013  BA8716 LCY-EDI 20:05-21:20 (Domestic), 01 hours 15 minutes
    10/11/2013  BA1464 LHR-EDI 21:00-22:25 (Domestic), 01 hours 25 minutes
    10/11/2013  BA1384 LHR-MAN 07:50-08:50 (Domestic), 01 hours 00 minutes
    10/11/2013  BA1390 LHR-MAN 11:10-12:15 (Domestic), 01 hours 05 minutes
    10/11/2013  BA1372 LHR-MAN 11:55-12:55 (Domestic), 01 hours 00 minutes
    10/11/2013  BA1394 LHR-MAN 13:10-14:10 (Domestic), 01 hours 00 minutes
    10/11/2013  BA1398 LHR-MAN 17:15-18:15 (Domestic), 01 hours 00 minutes
    10/11/2013  BA1376 LHR-MAN 20:05-21:05 (Domestic), 01 hours 00 minutes
    10/11/2013  BA1404 LHR-MAN 21:00-22:00 (Domestic), 01 hours 00 minutes
    10/11/2013  BA0826 LHR-DUB 15:35-16:50 (Club Europe), 01 hours 15 minutes
    10/11/2013  BA1324 LHR-NCL 07:35-08:45 (Domestic), 01 hours 10 minutes
    10/11/2013  BA1326 LHR-NCL 09:55-11:10 (Domestic), 01 hours 15 minutes
    10/11/2013  BA1332 LHR-NCL 12:40-13:55 (Domestic), 01 hours 15 minutes
    10/11/2013  BA1334 LHR-NCL 15:50-17:00 (Domestic), 01 hours 10 minutes
    10/11/2013  BA1336 LHR-NCL 18:25-19:35 (Domestic), 01 hours 10 minutes
    10/11/2013  BA1338 LHR-NCL 20:40-21:50 (Domestic), 01 hours 10 minutes

