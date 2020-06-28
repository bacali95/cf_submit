import os
import re

from prettytable import PrettyTable

from . import cf_login
from .cf_utils import Obj, read_data_from_file, write_data_to_file, obj_to_dict

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
groups_loc = os.path.join(cache_loc, 'groups.json')
config_loc = os.path.join(cache_loc, 'config.json')


def refresh_contests_data(group):
    browser = cf_login.login()
    browser.open('https://codeforces.com/group/%s/contests' % group)
    raw_html = browser.parsed
    rows = raw_html.find('div', class_='datatable').find(
        'table').find_all('tr')[1:]
    contests = []
    for row in rows:
        contest = Obj({})
        m = re.search('data-contestid=".*"', str(row))
        setattr(contest, 'id', m.group(0).replace('data-contestid="', '')[:-1])
        setattr(contest, 'name', row.find_all('td')[0].text.split('\n')[1].strip())
        contests.append(contest)
    return contests


def refresh_groups_data():
    browser = cf_login.login()
    config = read_data_from_file(config_loc)
    browser.open('https://codeforces.com/groups/with/%s' % (config.get('handle', None)))
    raw_html = browser.parsed
    rows = raw_html.find('div', class_='datatable').find('table').find_all('tr')[1:]
    groups = []
    for row in rows:
        if str(row.find_all('td')[2].text).strip() != 'Accepted':
            continue
        group = Obj({})
        setattr(group, 'id',
                re.sub(r'.*/group/', '', re.sub(r'/members.*', '', str(row.find('a', class_='groupName')))))
        setattr(group, 'name', str(row.find('a', class_='groupName').text).strip())
        groups.append(group)
    write_data_to_file(obj_to_dict(groups), groups_loc)


def load_contests(group_id, pretty_off):
    groups = [Obj(group) for group in read_data_from_file(groups_loc) or []]
    if len(groups) == 0:
        refresh_groups_data()
        groups = [Obj(group) for group in read_data_from_file(groups_loc) or []]
    group = next((group for group in groups if group.id == group_id), None)
    if group is None:
        return
    if not hasattr(group, 'contests'):
        setattr(group, 'contests', refresh_contests_data(group_id))
        write_data_to_file(obj_to_dict(groups), groups_loc)

    if pretty_off:
        print(' '.join(map(str, map(lambda contest: contest.id, group.contests))))
    else:
        print_pretty(group.contests)


def load_groups(pretty_off):
    groups = [Obj(group) for group in read_data_from_file(groups_loc) or []]
    if len(groups) == 0:
        refresh_groups_data()
        groups = [Obj(group) for group in read_data_from_file(groups_loc) or []]
    if pretty_off:
        print(' '.join(map(str, map(lambda group: group.id, groups))))
    else:
        print_pretty([group for group in groups])


def print_pretty(data):
    contests = PrettyTable()
    contests.field_names = ['Id', 'Name']
    for i in data:
        contests.add_row([i.id, i.name])
    contests.hrules = True
    contests.align['Name'] = 'l'
    print(contests.get_string(sortby='Id'))
