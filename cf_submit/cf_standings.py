import re

from prettytable import PrettyTable

from . import cf_login
from .cf_colors import Colors


def makeAscii(s):
    return re.sub(r'[^\x00-\x7f]', r'?', s)


# print friends standings in specified contest
# parse html
# gym contest
def print_standings(group, contest, verbose, top, sort, show_all):
    # requires login
    browser = cf_login.login()
    if group is not None:
        # group contest contest
        url = 'http://codeforces.com/group/' + \
              group + '/contest/' + contest + '/standings'
    elif len(str(contest)) >= 6:
        # gym contest
        url = 'http://codeforces.com/gym/' + contest + '/standings'
    else:
        # codeforces round
        url = 'http://codeforces.com/contest/' + contest + '/standings'
    # check if friends
    if group is not None:
        url += '/groupmates/true'
    elif show_all is False:
        url += '/friends/true'
    else:
        url += '/page/1'
    browser.open(url)
    raw_html = browser.parsed
    # get standings table
    handle_dict = {}
    mellon = raw_html.find('table', class_='standings').find_all('tr')

    standings = PrettyTable()

    # get header
    first_part = len(mellon[0].find_all('th')) - len(mellon[0].find_all('a'))
    header = []
    if verbose:
        for h_cell in mellon[0].find_all('th')[:first_part]:
            h_cell_str = str(h_cell.get_text(strip=True))
            if h_cell_str == '*':
                h_cell_str = 'Hacks'
            header.append(h_cell_str)
    else:
        for h_cell in mellon[0].find_all('th')[1:3]:
            header.append(str(h_cell.get_text(strip=True)))
    for h_cell in mellon[0].find_all('a'):
        header.append(str(h_cell.get_text(strip=True)))
    # append sorter to header
    if sort is not None:
        header.append('sorter')
    standings.field_names = header

    id_start = 4
    if not verbose:
        id_start = 0
        for h_cell in mellon[0].find_all('th'):
            h_cell_str = str(h_cell.get_text(strip=True))
            if h_cell_str.find('A') != -1:
                break
            id_start += 1

    fields = dict()
    for i, h in enumerate(header):
        fields[h] = i

    # find problem start and solve column
    problem_start = 0
    while header[problem_start].find('A') == -1:
        problem_start += 1
    solve_col = 0
    while header[solve_col] != '=':
        solve_col += 1

    # if sort, use dict
    if sort is not None:
        handle_dict = {}

    # fix top
    top = min(top + 1, len(mellon) - 1)

    # iterate
    for ami in mellon[1:top]:
        virtual = True
        row = ami.find_all('td')
        table_row = []
        # get place
        # this cell has problems
        rank = str(row[0].get_text(strip=True))
        if len(rank) == 0:
            virtual = False
        if verbose:
            if rank.find(')') != -1:
                rank = rank[rank.find('(') + 1:rank.find(')')]
            table_row.append(rank)

        # get name
        party = str(row[1].get_text(strip=True))
        if verbose:
            team = []
            # check if virtual time colon
            virtual_time = None
            if party[-3] == ':':
                virtual_time = party[-5:]
                party = party[:-5]

            # check if there are still colons left if yes, split at last colon
            if party.count(':') > 0:
                # check for '#'
                tail = ''
                if party[-1] == '#':
                    tail = '#'
                    party = party[:-1]
                # split
                party = party.split(':')
                # get first part (team name)
                team_name = party[0]
                for party_part in party[1:-1]:
                    team_name += ':' + party_part
                if len(team_name + tail) > 24:
                    team_name = team_name[:20] + '...'
                team_name += tail + ':'
                team.append(team_name)
                # split rest of team members
                for member in party[-1].split(','):
                    team.append(member.strip())
            else:
                team.append(party)
            # append time if it exists'''
            if virtual_time is not None:
                team.append(virtual_time)
            # join party
            party = '\n'.join(team)
        else:
            if party[-3] == ':':
                party = party[:-5]
            if party.count(':') > 0:
                tail = ''
                if party[-1] == '#':
                    tail = '#'
                    party = party[:-1]
                # split
                party = party.split(':')
                team_name = party[0]
                for party_part in party[1:-1]:
                    team_name += ':' + party_part
                if len(team_name) > 32:
                    team_name = team_name[:32] + '...'
                team_name += tail
                party = team_name
        table_row.append(makeAscii(party))

        # get points or number of solves
        table_row.append(int(str(row[2].get_text(strip=True))))
        # get penalty or hacks
        if verbose:
            table_row.append(str(row[3].get_text(strip=True)))

        # get problem submissions
        for cell in row[id_start:]:
            problem_res = str(cell.get_text(strip=True))
            if virtual and len(problem_res) > 5:
                if verbose:
                    problem_res = (problem_res[:-5] + '\n' + problem_res[-5:])
                else:
                    problem_res = problem_res[:-5]
            else:
                problem_res = problem_res.replace('-', 'WA-')
            table_row.append(problem_res)

        # check sort
        if sort is not None:
            # add to dict
            # make party legible
            if party[0] == '*':
                party = party[1:]
            if party[-1] == '#':
                party = party[:-1]

            # check if party exists
            if party not in handle_dict:
                handle_dict[party] = table_row
            else:
                # update
                for i in range(problem_start, len(header) - 1):
                    # update if empty or wa
                    if len(handle_dict[party][i]) == 0:
                        handle_dict[party][i] = table_row[i]
                        # check if we should update solve_col
                        if len(table_row[i]) != 0 and table_row[i][0] == '+':
                            handle_dict[party][solve_col] += 1
                    elif handle_dict[party][i][0] != '+' and len(table_row[i]) != 0:
                        total_wa = int(handle_dict[party][i].split(
                            '\n')[0].split('-')[1])
                        if table_row[i].find('-') != -1:
                            # add wa
                            total_wa += int(table_row[i].split('\n')[0].split('-')[1])
                            handle_dict[party][i] = 'WA-' + str(total_wa)
                        else:
                            # add wa to correct submission
                            correct = table_row[i].split('\n')[0][1:]
                            if len(correct) != 0:
                                total_wa += int(correct)
                            handle_dict[party][i] = '+' + str(total_wa)
                            # update solve_col
                            handle_dict[party][solve_col] += 1
        else:
            # NO sort, add to table_row
            standings.add_row(table_row)

    # standings properties
    if verbose:
        standings.hrules = True
        if 'Penalty' in standings.align:
            standings.align['Penalty'] = 'r'
    standings.align['Who'] = 'l'
    standings.align['='] = 'r'

    # print standings
    if sort is None:
        print(standings)

    elif sort == 'solves':
        # add row_info to standings
        for _, row_info in handle_dict.items():
            # append the sorter
            sort_value = row_info[fields['=']]
            if 'Penalty' in fields:
                if len(row_info[fields['Penalty']]) == 0:
                    sort_value = 100000 * sort_value - 99999
                else:
                    sort_value = 100000 * sort_value - \
                                 int(row_info[fields['Penalty']])
            row_info.append(sort_value)
            standings.add_row(row_info)
        # print
        print(standings.get_string(
            sortby='sorter',
            reversesort=True,
            fields=header[:-1]
        ))

    elif sort == 'index':
        print('sort == index : nothing here')

    else:
        print('this should not have happened. nothing here')

    # first check if countdown
    # bold_start = '\033[1m'
    # bold_end = '\033[0;0m'
    countdown_timer = raw_html.find_all('span', class_='countdown')
    if len(countdown_timer) > 0:
        print('%sTIME LEFT: %s%s' % (Colors.BOLD, str(countdown_timer[0].get_text(strip=True)), Colors.END))


# get time
def print_time(group, contest):
    browser = cf_login.login()
    if contest is None:
        print('Set contest first with: cf con/gym --id 1111')
        return
    if group is not None:
        url = 'http://codeforces.com/group/' + group + '/contest/' + contest + '/submit'
    elif len(str(contest)) >= 6:
        url = 'http://codeforces.com/gym/' + contest + '/submit'
    else:
        url = 'http://codeforces.com/contest/' + contest + '/submit'
    browser.open(url)
    countdown_timer = browser.parsed.find_all(
        'span', class_='contest-state-regular countdown before-contest-' + contest + '-finish')
    if len(countdown_timer) == 0:
        print('Contest ' + contest + ' is over')
    else:
        print('%sTIME LEFT: %s%s' % (Colors.BOLD, str(countdown_timer[0].get_text(strip=True)), Colors.END))
