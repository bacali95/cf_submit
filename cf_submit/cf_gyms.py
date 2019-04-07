import os
import requests
from prettytable import PrettyTable
from threading import Thread

from . import cf_io_utils

URL = 'https://codeforces.com/api/contest.list'
PARAMS = {'gym': 'true'}
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, "config.json")
gyms_loc = os.path.join(cache_loc, "gyms.json")
config = cf_io_utils.read_data_from_file(config_loc)


def refresh_gyms_data():
    try:
        r = requests.get(url=URL, params=PARAMS, timeout=4).json()
        data = [gym for gym in r["result"] if len(str(gym['id'])) == 6]
        cf_io_utils.write_data_in_file(data, gyms_loc)
    except:
        return


def load_gyms(pretty_off):
    Thread(target=refresh_gyms_data).start()
    data = cf_io_utils.read_data_from_file(gyms_loc) or []
    data.sort(key=lambda x: x['id'], reverse=True)
    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data)
    else:
        print_pretty(data[0:20])


def print_pretty(data):
    gyms = PrettyTable()
    gyms.field_names = ['Id', 'Name']
    for i in data:
        gyms.add_row([i['id'], i['name']])
    gyms.hrules = True
    gyms.align["Name"] = "l"
    print(gyms.get_string(sortby="Id", reversesort=True))
