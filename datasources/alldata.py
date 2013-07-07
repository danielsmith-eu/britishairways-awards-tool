import os, json
from datasources.oneworld import Oneworld

class AllData:
    """ Class to load all data from all sources, and cache results.
    """

    def __init__(self, cache_dir="cache"):
        """ Load all data sources, and cache results.
        """

        self.cache_dir = cache_dir

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        def get_ow():
            ow = Oneworld()
            ow_data = ow.get_all_data()
            return ow_data

        sources = [
            ("oneworld", get_ow),
        ]

        self.data = {}
        for source in sources:
            src_name, src_func = source
            self.data[src_name] = self.cached(src_name, src_func)


    def get_data(self):
        """ Return all data as single structure.
        """

        return self.data


    def cached(self, filename, func):
        """ Look for data from filename and load it, or call func to get the data if not already cached.
        """

        path = "{0}/{1}".format(self.cache_dir, filename)
        if os.path.exists(path):
            f = open(path, "r")
            data = json.load(f)
            f.close()
            return data
        else:
            data = func()
            f = open(path, "w")
            json.dump(data, f)
            f.close()
            return data

