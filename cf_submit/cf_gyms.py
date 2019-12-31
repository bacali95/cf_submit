import os
from prettytable import PrettyTable
from threading import Thread

from .cf_utils import readDataFromFile, writeDataToFile
from .codeforces import CodeforcesAPI

codeforces = CodeforcesAPI()
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
gyms_loc = os.path.join(cache_loc, 'gyms.json')


def refresh_gyms_data():
    try:
        writeDataToFile(codeforces.gymList(), gyms_loc)
    except Exception:
        return


def load_gyms(pretty_off):
    data = readDataFromFile(gyms_loc) or []
    if len(data) == 0:
        refresh_gyms_data()
        data = readDataFromFile(gyms_loc) or []
    else:
        Thread(target=refresh_gyms_data).start()
    data.sort(key=lambda x: x['id'], reverse=True)
    if pretty_off:
        print(' '.join(map(str, map(lambda x: x['id'], data))))
    else:
        print_pretty(data[0:20])


def print_pretty(data):
    gyms = PrettyTable()
    gyms.field_names = ['Id', 'Name']
    for i in data:
        gyms.add_row([i['id'], i['name']])
    gyms.hrules = True
    gyms.align['Name'] = 'l'
    print(gyms.get_string(sortby='Id', reversesort=True))
