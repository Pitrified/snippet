# absolute import of the function
from sample.some_lib.some_functions import list_good_add

# leave more context, use the functions inside some_utils explicitly
from sample.some_lib import some_utils

# relative import
from ..some_lib.some_functions import list_slow_add


class ListTracker:
    def __init__(self):
        self.total = 0
        self.slow_total = 0

    def new_list(self, l):
        new_total = list_good_add(l)
        self.total = some_utils.good_add(self.total, new_total)

        alternative_total = list_slow_add(l)
        self.slow_total += alternative_total
