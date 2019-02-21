import requests
from prettytable import PrettyTable
from . import cf_login


def load_groups(pretty_off):
    browser = cf_login.login()
    handle = cf_login.get_secret(False)
    browser.open("https://codeforces.com/groups/with/%s" % (handle))
    rows = browser.find("div", class_="datatable").find(
        "table").find_all("tr")[1:]
    data = []
    for row in rows:
        text = row.find("a", class_="groupName")
        data.append(dict(id=str(text.get("href")).replace(
            "/group/", "").replace("/members", ""), name=text.text))
    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data)
    else:
        print_pretty(data)


def load_contests(group, pretty_off):
    browser = cf_login.login()
    print(group)
    browser.open("https://codeforces.com/group/%s/contests" % (group))
    rows = browser.find("div", class_="datatable").find(
        "table").find_all("tr")[1:]
    data = []
    for row in rows:
        text = str(row.find_all("td")[0]).replace("<td>", "")
        data.append(dict(id=row.get('data-contestid'),
                         name=text[0:text.find("<br")].strip()))
    if pretty_off:
        data = list(map(lambda x: x['id'], data))
        print(*data)
    else:
        print_pretty(data)


def print_pretty(data):
    contests = PrettyTable()
    contests.field_names = ['Id', 'Name']
    for i in data:
        contests.add_row([i['id'], i['name']])
    contests.hrules = True
    contests.align["Name"] = "l"
    print(contests.get_string())
