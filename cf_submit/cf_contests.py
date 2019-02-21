import requests
from prettytable import PrettyTable


def load_contests(gym, curr, pretty_off):
    if gym:
        response = requests.get(
            url="https://codeforces.com/api/contest.list?gym=true")
    else:
        response = requests.get(
            url="https://codeforces.com/api/contest.list?gym=false")
    result = response.json()['result']
    if gym:
        data = list(filter(lambda x: str(x['id']).startswith(
            curr) and len(str(x['id'])) == 6, result))
    else:
        data = list(filter(lambda x: str(x['id']).startswith(curr), result))

    data.sort(key=lambda x: x['id'], reverse=True)

    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data[0:20])
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
