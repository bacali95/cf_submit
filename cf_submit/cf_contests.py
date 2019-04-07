import os
import requests
from prettytable import PrettyTable

from . import cf_io_utils

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, "config.json")
config = cf_io_utils.read_data_from_file(config_loc)


def load_contests(pretty_off):
    data = config.get("contests", [])
    data.sort(key=lambda x: x['id'], reverse=True)
    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data[0:20])
    else:
        print_pretty(data[0:20])


def print_pretty(data):
    contests = PrettyTable()
    contests.field_names = ['Id', 'Name']
    for i in data:
        contests.add_row([i['id'], i['name']])
    contests.hrules = True
    contests.align["Name"] = "l"
    print(contests.get_string(sortby="Id", reversesort=True))
