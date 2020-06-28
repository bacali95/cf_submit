import os
from threading import Thread

from prettytable import PrettyTable

from .cf_utils import read_data_from_file, write_data_to_file, Obj, obj_to_dict
from .codeforces import CodeforcesAPI

codeforces = CodeforcesAPI()
cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
gyms_loc = os.path.join(cache_loc, 'gyms.json')


def load_gyms(pretty_off):
    gyms = [Obj(gym) for gym in read_data_from_file(gyms_loc) or []]
    if len(gyms) == 0:
        write_data_to_file(obj_to_dict(codeforces.gymList()), gyms_loc)
        gyms = [Obj(gym) for gym in read_data_from_file(gyms_loc) or []]
    else:
        Thread(target=write_data_to_file, args=(codeforces.gymList(), gyms_loc)).start()
    gyms.sort(key=lambda gym: gym.id, reverse=True)
    if pretty_off:
        print(' '.join(map(str, map(lambda x: x.id, gyms))))
    else:
        print_pretty(gyms[0:20])


def print_pretty(gyms):
    gyms_table = PrettyTable()
    gyms_table.field_names = ['Id', 'Name']
    for gym in gyms:
        gyms_table.add_row([gym.id, gym.name])
    gyms_table.hrules = True
    gyms_table.align['Name'] = 'l'
    print(gyms_table.get_string(sortby='Id', reversesort=True))
