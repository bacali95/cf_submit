import os
from prettytable import PrettyTable

from . import cf_io_utils
from . import cf_login
from .cf_colors import colors

cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
config_loc = os.path.join(cache_loc, 'config.json')
problems_loc = os.path.join(cache_loc, 'problems.json')
config = cf_io_utils.read_data_from_file(config_loc)
contest = config.get('contest', None)
group = config.get('group', None)


def refresh_problems_data():
    browser = cf_login.login()
    if group is not None:
        url = 'http://codeforces.com/group/' + group + '/contest/' + contest
    elif len(str(contest)) >= 6:
        url = 'http://codeforces.com/gym/' + contest
    else:
        url = 'http://codeforces.com/contest/' + contest
    browser.open(url)
    raw_html = browser.parsed
    data = []
    probraw = raw_html.find_all('table', class_='problems')[0].find_all('tr')
    for row in probraw[1:]:
        cell = row.find_all('td')
        if len(cell) < 4:
            continue
        problem = {}
        problem['id'] = str(cell[0].get_text(strip=True))
        problem['name'] = str(cell[1].find('a').get_text(strip=True))
        nbr_solves = str(cell[3].get_text(strip=True))
        if len(nbr_solves) == 0:
            problem['solves'] = int(0)
        else:
            problem['solves'] = int(nbr_solves[1:])
        data.append(problem)
    return data


def load_problems(pretty_off):
    if contest is None:
        print("Set contest first with: cf con --id 1111")
        return

    problems = cf_io_utils.read_data_from_file(problems_loc) or {}
    if problems.get(contest, None) is None:
        problems[contest] = refresh_problems_data()
        cf_io_utils.write_data_in_file(problems, problems_loc)
    # printing
    if pretty_off:
        ids = [str(problem['id']).lower() for problem in problems[contest]]
        print(*ids)
    else:
        print_pretty(problems[contest])


def print_pretty(data):
    problems = PrettyTable()
    problems.field_names = ['Id', 'Name', 'Solves']
    for i in data:
        problems.add_row([i['id'], i['name'], i['solves']])
    problems.align['Name'] = 'l'
    problems.align['Solves'] = 'r'
    print(problems.get_string(sortby='Id'))
