import os
from prettytable import PrettyTable
from threading import Thread

from .cf_utils import readDataFromFile, writeDataToFile
from .codeforces import CodeforcesAPI

codeforces = CodeforcesAPI()
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
contests_loc = os.path.join(cache_loc, 'contests.json')


def refresh_contests_data():
    try:
        writeDataToFile(codeforces.contestList(), contests_loc)
    except Exception:
        return


def load_contests(pretty_off):
    data = readDataFromFile(contests_loc) or []
    if len(data) == 0:
        refresh_contests_data()
        data = readDataFromFile(contests_loc) or []
    else:
        Thread(target=refresh_contests_data).start()
    data.sort(key=lambda x: x['id'], reverse=True)
    if pretty_off:
        print(' '.join(map(str, map(lambda x: x['id'], data))))
    else:
        print_pretty(data[0:20])


def print_pretty(data):
    contests = PrettyTable()
    contests.field_names = ['Id', 'Name']
    for i in data:
        contests.add_row([i['id'], i['name']])
    contests.hrules = True
    contests.align['Name'] = 'l'
    print(contests.get_string(sortby='Id', reversesort=True))
