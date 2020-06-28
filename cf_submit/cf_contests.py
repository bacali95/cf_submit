import os
from threading import Thread

from prettytable import PrettyTable

from .cf_utils import read_data_from_file, write_data_to_file, Obj, obj_to_dict
from .codeforces import CodeforcesAPI

codeforces = CodeforcesAPI()
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
contests_loc = os.path.join(cache_loc, 'contests.json')


def load_contests(pretty_off):
    contests = [Obj(contest) for contest in read_data_from_file(contests_loc) or []]
    if len(contests) == 0:
        write_data_to_file(obj_to_dict(codeforces.contestList()), contests_loc)
        contests = [Obj(contest) for contest in read_data_from_file(contests_loc) or []]
    else:
        Thread(target=write_data_to_file, args=(codeforces.contestList(), contests_loc)).start()
    contests.sort(key=lambda contest: contest.id, reverse=True)
    if pretty_off:
        print(' '.join(map(str, map(lambda x: x.id, contests))))
    else:
        print_pretty(contests[0:20])


def print_pretty(contests):
    contests_table = PrettyTable()
    contests_table.field_names = ['Id', 'Name']
    for contest in contests:
        contests_table.add_row([contest.id, contest.name])
    contests_table.hrules = True
    contests_table.align['Name'] = 'l'
    print(contests_table.get_string(sortby='Id', reversesort=True))
