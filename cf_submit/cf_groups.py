import requests
import os
import re
from prettytable import PrettyTable

from . import cf_login
from . import cf_io_utils

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
groups_loc = os.path.join(cache_loc, 'groups.json')
config_loc = os.path.join(cache_loc, "config.json")
config = cf_io_utils.read_data_from_file(config_loc)


def refresh_contests_data(group):
    browser = cf_login.login()
    browser.open('https://codeforces.com/group/%s/contests'
                 % (group))
    raw_html = browser.parsed
    rows = raw_html.find('div', class_='datatable').find(
        'table').find_all('tr')[1:]
    contests = []
    for row in rows:
        contest = {}
        m = re.search('data-contestid=".*"', str(row))
        contest['id'] = m.group(0).replace('data-contestid="', '')[:-1]
        contest['name'] = row.find_all('td')[0].text.split('\n')[1].strip()
        contests.append(contest)
    return contests


def refresh_groups_data():
    browser = cf_login.login()
    browser.open('https://codeforces.com/groups/with/%s' %
                 (config.get('handle', None)))
    raw_html = browser.parsed
    rows = raw_html.find('div', class_='datatable').find(
        'table').find_all('tr')[1:]
    data = {}
    for row in rows:
        if str(row.find_all('td')[2].text).strip() != 'Accepted':
            continue
        group = {}
        id = str(row.find('a', class_='groupName'))
        id = re.sub(r'.*/group/', '', id)
        id = re.sub(r'/members.*', '', id)
        group['id'] = id
        group['name'] = str(row.find('a', class_='groupName').text).strip()
        data[id] = group
    return data


def load_contests(group, pretty_off):
    groups = cf_io_utils.read_data_from_file(groups_loc)
    if groups is None:
        groups = refresh_groups_data()
        cf_io_utils.write_data_in_file(groups, groups_loc)
    if groups.get(group, None) is None:
        return
    if groups[group].get('contests', None) is None:
        groups[group]['contests'] = refresh_contests_data(group)
        cf_io_utils.write_data_in_file(groups, groups_loc)

    if pretty_off:
        ids = [contest['id'] for contest in groups[group]['contests']]
        print(*ids)
    else:
        print_pretty(groups[group]['contests'])


def load_groups(pretty_off):
    groups = cf_io_utils.read_data_from_file(groups_loc)
    if groups is None:
        groups = refresh_groups_data()
        cf_io_utils.write_data_in_file(groups, groups_loc)

    if pretty_off:
        ids = [id for id in groups]
        print(*ids)
    else:
        print_pretty(groups.values())


def print_pretty(data):
    contests = PrettyTable()
    contests.field_names = ['Id', 'Name']
    for i in data:
        contests.add_row([i['id'], i['name']])
    contests.hrules = True
    contests.align['Name'] = 'l'
    print(contests.get_string(sortby='Id'))
