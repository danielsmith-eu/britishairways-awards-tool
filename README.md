britishairways-awards-tool
==========================

A tool for searching British Airways/Avios awards more easily

Usage:

    Look up oneworld award flight availability via British Airways.

    positional arguments:
      from          Departure Airport (3-letter Code, e.g. LHR)
      dates         Date or Date Range in DD/MM/YYYY or DD/MM/YYYY-DD/MM/YYYY format
      class         Class of travel as 1-letter code, where Economy=M, Premium
                    Economy=W, Business=C and First=F
      adults        Number of adults

    optional arguments:
      -h, --help    show this help message and exit
      --to TO       Arrival Airport (3-letter Code, e.g. LHR), leave blank to find
                    all oneworld flights from the departure city. Comma separate
                    multiple airportsm e.g. EDI,MAN,DUB,NCL
      --debug       Enable verbose logging
      --info        Show information as searches are performed
      --directonly  Ignore results that are made up of multiple segments




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

Example showing flights from multiple departure points, on multiple days, in multiple classes:

    $ python tool.py LAX,LAS --to LON 23/08/2013-25/08/2013 W,C,F 2
