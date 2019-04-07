import requests
import os
from prettytable import PrettyTable

from . import cf_login
from . import cf_io_utils

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, "config.json")
config = cf_io_utils.read_data_from_file(config_loc)


def load_groups(pretty_off):
    data = config.get("groups", [])
    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data)
    else:
        print_pretty(data)


def print_pretty(data):
    contests = PrettyTable()
    contests.field_names = ['Id', 'Name']
    for i in data:
        contests.add_row([i['id'], i['name']])
    contests.hrules = True
    contests.align["Name"] = "l"
    print(contests.get_string())
