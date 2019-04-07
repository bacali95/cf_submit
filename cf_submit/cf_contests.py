import os
import requests
from prettytable import PrettyTable
from threading import Thread

from . import cf_io_utils

URL = 'https://codeforces.com/api/contest.list'
PARAMS = {'gym': 'false'}
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, "config.json")
contests_loc = os.path.join(cache_loc, "contests.json")
config = cf_io_utils.read_data_from_file(config_loc)


def refresh_contests_data():
    try:
        r = requests.get(url=URL, params=PARAMS, timeout=0.5).json()
        cf_io_utils.write_data_in_file(r["result"], contests_loc)
    except:
        return


def load_contests(pretty_off):
    Thread(target=refresh_contests_data).start()
    data = cf_io_utils.read_data_from_file(contests_loc) or []
    data.sort(key=lambda x: x['id'], reverse=True)
    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data)
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
