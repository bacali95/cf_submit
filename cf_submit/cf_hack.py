import os
import re
import time
from subprocess import Popen, TimeoutExpired

import javalang
from javalang.tree import ClassDeclaration
from prettytable import PrettyTable
from robobrowser import RoboBrowser

from . import cf_login
from .cf_colors import Colors
from .cf_utils import safe_list_get
from .codeforces import CodeforcesAPI

dir_path = os.getcwd()


# Hack problems
def begin_hack(contest, problem, generator, tle_generator, checker, correct_solution, max_tests, reverse, time_limit):
    # Preparing Workspace
    init_hack_dir(generator, tle_generator, checker, correct_solution)
    generator = 'workspace/%s' % generator
    checker = 'workspace/%s' % checker
    correct_solution = 'workspace/%s' % correct_solution
    if tle_generator is not None:
        tle_generator = 'workspace/%s' % tle_generator

    with open('tried_submissions', 'r') as file:
        list_str = file.read().strip()
        tried_submissions = list()
        if list_str != '':
            tried_submissions = list(map(int, list_str.split(' ')))
    tried_submissions_file = open('tried_submissions', 'a')

    tried_solutions = 0
    hacked_solutions = 0

    browser = get_browser_for_url(
        'https://codeforces.com/contest/%s/status/%s' % (contest, problem))
    max_pages = int(browser.parsed.find_all(class_='page-index')[-1].text)
    print('\n%sHappy Hacking 3:) - max pages : %s%s' %
          (Colors.HEADER, max_pages, Colors.END))
    start = max_pages if reverse else 1
    stop = 0 if reverse else max_pages + 1
    for i in range(start, stop, -1 if reverse else 1):
        try:
            browser = get_browser_for_url(
                'https://codeforces.com/contest/%s/status/%s/page/%s?order=BY_CONSUMED_TIME_ASC'
                % (contest, problem, i))
            submissions = browser.parsed.find_all(
                'table', class_='status-frame-datatable')[0].find_all('tr')[1:]
            for submission in submissions:
                try:
                    submission_id = int(submission.find(
                        'td', class_='id-cell').find('a').text)
                    if submission_id in tried_submissions:
                        print('\n%sSubmission %d on page %d/%d already tried!!%s' %
                              (Colors.WARNING, submission_id, i, max_pages, Colors.END))
                        continue
                    language = submission.find_all(
                        'td')[4].text.strip().replace(' ', '')
                    browser = get_browser_for_url(
                        'http://codeforces.com/contest/%s/submission/%d' % (contest, submission_id))
                    if len(browser.parsed.find_all('pre', class_='program-source')) > 0:
                        Popen(['rm', '-rf', 'workspace/testing_dir']).wait()
                        Popen(['mkdir', '-p', 'workspace/testing_dir']).wait()

                        source = browser.parsed.find_all(
                            'pre', class_='program-source')[0].text
                        player_solution = create_player_solution_file(
                            source, get_language_key(language))
                        if player_solution is None:
                            continue

                        print('\n%sHacked : %d, %sFailed : %d, %sTotal : %d%s'
                              % (Colors.OK_GREEN, hacked_solutions, Colors.FAIL, tried_solutions - hacked_solutions,
                                 Colors.OK_BLUE, tried_solutions, Colors.END))
                        print('%sTrying to hack a %s solution - %d on page %d/%d...%s'
                              % (Colors.HEADER, language, submission_id, i, max_pages, Colors.END))
                        print('%sNormal hack process%s' %
                              (Colors.WARNING, Colors.END))

                        comp(player_solution)
                        language = get_language_key(language)
                        result = execute_hack_process(generator, checker, correct_solution, player_solution,
                                                      language, time_limit, max_tests)
                        if result == 'CHECKER_ERROR':
                            test_hack_loc = os.path.join(
                                dir_path, 'workspace/testing_dir/test.in')
                            print('%sHope that will win 3:)%s' %
                                  (Colors.OK_GREEN, Colors.END))
                            submit_hack(contest, test_hack_loc, submission_id)
                            hacked_solutions = hacked_solutions + 1
                            tried_submissions_file.write(' %s' % submission_id)
                            tried_submissions_file.flush()
                            continue

                        if tle_generator is not None:
                            print(
                                '%sTLE hack process with time limit %ss %s' % (Colors.WARNING, time_limit, Colors.END))
                            result = execute_hack_process(tle_generator, checker, correct_solution, player_solution,
                                                          language, time_limit)
                            if result in ['CHECKER_ERROR', 'TIME_LIMIT_EXCEEDED']:
                                test_hack_loc = os.path.join(
                                    dir_path, tle_generator)
                                print('%sHope that will win 3:)%s' %
                                      (Colors.OK_GREEN, Colors.END))
                                submit_tle_hack(
                                    contest, test_hack_loc, submission_id)
                                hacked_solutions = hacked_solutions + 1
                                tried_submissions_file.write(
                                    ' %s' % submission_id)
                                tried_submissions_file.flush()
                                continue

                        tried_solutions = tried_solutions + 1
                        tried_submissions_file.write(' %s' % submission_id)
                        tried_submissions_file.flush()
                except KeyboardInterrupt:
                    time.sleep(2)
                    break
                except Exception:
                    continue
        except KeyboardInterrupt:
            time.sleep(2)
            break
        except Exception:
            continue
    print('\n%sRESULT => %sHacked : %d, %sFailed : %d, %sTotal : %d'
          % (Colors.HEADER, Colors.OK_GREEN, hacked_solutions, Colors.FAIL,
             tried_solutions - hacked_solutions, Colors.OK_BLUE, tried_solutions))


def submit_hack(contest, hack_test, submission_id):
    browser = cf_login.login()
    browser.open('https://codeforces.com/contest/' +
                 contest + '/challenge/' + str(submission_id))
    hack_form = browser.get_form(class_='challenge-form')
    hack_form['testcaseFromFile'] = hack_test
    browser.submit_form(hack_form)


def submit_tle_hack(contest, hack_generator, submission_id):
    browser = cf_login.login()
    browser.open('https://codeforces.com/contest/' +
                 contest + '/challenge/' + str(submission_id))
    hack_form = browser.get_form(class_='challenge-form')
    hack_form['generatorSourceFile'] = hack_generator
    hack_form['programTypeId'] = '50'
    browser.submit_form(hack_form)


def comp(source):
    info = source.split('.')
    lang = info[-1]
    f_null = open(os.devnull, 'w')
    if lang == 'cpp':
        Popen('g++ %s -DONLINE_JUDGE -o %s' % (source, info[0]), stdout=f_null, stderr=f_null, shell=True).wait()
    elif lang == 'c':
        Popen('gcc %s -DONLINE_JUDGE -o %s' % (source, info[0]), stdout=f_null, stderr=f_null, shell=True).wait()
    elif lang == 'java':
        Popen('javac %s' % source, stdout=f_null, stderr=f_null, shell=True).wait()
    elif lang == 'kt':
        Popen('kotlinc %s -include-runtime -d %s' % (source, info[0] + '.jar'), stdout=f_null, stderr=f_null,
              shell=True).wait()


def execute(source, args=None, language=None, input_file=None, output_file=None, timeout=10):
    if args is None:
        args = []
    executable = source.split('.')[0]
    if language is None:
        language = source.split('.')[-1]
        language = 'py3' if language == 'py' else language
    if language in ['cpp', 'c']:
        cmd = './%s ' % executable
    elif language == 'java':
        cmd = 'java -DONLINE_JUDGE %s ' % executable
    elif language == 'kt':
        cmd = 'java -DONLINE_JUDGE -jar %s.jar ' % executable
    elif language == 'py2':
        cmd = 'python2 %s ' % source
    elif language == 'py3':
        cmd = 'python3 %s ' % source
    else:
        print('Sorry language not supported!')
        return exit(-1)
    return_code = -1
    process = None
    try:
        process = Popen(cmd + ' '.join(list(map(str, args))), stdin=input_file, stdout=output_file, shell=True)
        process.wait(int(timeout))
        return_code = process.returncode
    except TimeoutExpired:
        process.kill()
        return_code = 98989898
    except Exception:
        return_code = -1
    finally:
        return return_code


def execute_hack_process(generator, checker, correct_solution, player_solution, player_language, time_limit,
                         max_tests=1):
    for test_index in range(0, max_tests):
        input_file = open('workspace/testing_dir/test.in', 'w')
        return_code = execute(generator, args=[test_index], output_file=input_file)
        if return_code != 0:
            return 'GENERATOR_ERROR'

        input_file = open('workspace/testing_dir/test.in', 'r')
        answer_file = open('workspace/testing_dir/test.ans', 'w')
        return_code = execute(correct_solution, input_file=input_file, output_file=answer_file)
        if return_code != 0:
            return 'CORRECT_SOLUTION_ERROR'

        output_file = open('workspace/testing_dir/test.out', 'w')
        return_code = execute(player_solution, language=player_language, args=['<', 'workspace/testing_dir/test.in'],
                              output_file=output_file, timeout=time_limit)

        if return_code == 98989898:
            return 'TIME_LIMIT_EXCEEDED'

        if return_code != 0:
            return 'PLAYER_SOLUTION_ERROR'

        return_code = execute(checker, args=['workspace/testing_dir/test.in', 'workspace/testing_dir/test.out',
                                             'workspace/testing_dir/test.ans'])
        if return_code != 0:
            return 'CHECKER_ERROR'
    return 'ALL_TESTS_PASSED'


def init_hack_dir(generator, tle_generator, checker, correct_solution):
    print('%sInitializing workspace...%s' % (Colors.OK_GREEN, Colors.END))
    Popen(['touch', 'tried_submissions']).wait()
    Popen(['rm', '-rf', 'workspace']).wait()
    Popen(['mkdir', '-p', 'workspace']).wait()
    Popen(['cp', 'testlib.h', 'workspace']).wait()
    Popen(['cp', generator, 'workspace']).wait()
    Popen(['cp', checker, 'workspace']).wait()
    Popen(['cp', correct_solution, 'workspace']).wait()

    comp('workspace/%s' % generator)
    comp('workspace/%s' % checker)
    comp('workspace/%s' % correct_solution)
    if tle_generator is not None:
        Popen(['cp', tle_generator, 'workspace']).wait()
        comp('workspace/%s' % tle_generator)

    print('%sWorkspace is ready!!%s' % (Colors.OK_GREEN, Colors.END))


def get_browser_for_url(url):
    browser = RoboBrowser(parser='lxml')
    browser.open(url)
    return browser


def get_language_key(language):
    if re.match(r'(.)*\+\+(.)*', language):
        return 'cpp'
    elif re.match(r'(.)*GNU(.)*', language):
        return 'c'
    elif re.match(r'(.)*Kotlin(.)*', language):
        return 'c'
    elif re.match(r'(.)*Java(.)*', language):
        return 'java'
    elif re.match(r'(.)*Kotlin(.)*', language):
        return 'kt'
    elif re.match(r'(.)*Py(.)*2', language):
        return 'py2'
    elif re.match(r'(.)*Py(.)*3', language):
        return 'py3'
    else:
        return None


def create_player_solution_file(source, language):
    if language == 'cpp':
        file_name = 'noncorrect.cpp'
    elif language == 'c':
        file_name = 'noncorrect.c'
    elif language == 'kt':
        file_name = 'noncorrect.kt'
        source = 'package workspace.testing_dir;\n' + source
    elif language == 'java':
        try:
            tree = javalang.parse.parse(source)
            name = next(klass.name for klass in tree.types
                        if isinstance(klass, ClassDeclaration)
                        for m in klass.methods
                        if m.name == 'main' and m.modifiers.issuperset({'public', 'static'}))
            file_name = name + '.java'
            source = 'package workspace.testing_dir;\n' + source
        except TypeError:
            return None
    elif language in ['py2', 'py3']:
        file_name = 'noncorrect.py'
    else:
        return None
    file_name = 'workspace/testing_dir/%s' % file_name
    for_hack_source = open(file_name, 'w')
    for_hack_source.write(source)
    for_hack_source.close()
    return file_name


def print_standings(contest, limit, show_all):
    if contest is None:
        print('Please specify a contest first using: cf hack standings --contest 1010 or cf con --id 1010')
        return
    codeforces = CodeforcesAPI()
    standings = codeforces.contestStandings(
        contest, count=None, show_unofficial=True)
    rows = standings.rows
    print('Contest:\n   Id:   %s\n   Name: %s' %
          (contest, standings.contest.name))
    data = list()
    standings = PrettyTable()
    standings.field_names = ['Rank', 'Name', 'Hacks']
    standings.align['Name'] = 'l'
    standings.align['Hacks'] = 'l'
    for row in rows:
        if row.party.ghost is True:
            handle = row.party.teamName
        else:
            handle = safe_list_get(row.party.members, 0, {'handle': None}).handle
        entry = {
            'handle': handle,
            'successfulHackCount': row.successfulHackCount,
            'unsuccessfulHackCount': row.unsuccessfulHackCount
        }
        data.append(entry)

    data.sort(key=lambda elem: elem['unsuccessfulHackCount'])
    data.sort(key=lambda elem: elem['successfulHackCount'], reverse=True)
    for i, item in enumerate(data):
        if i >= limit and not show_all:
            break
        standings.add_row(
            [i + 1, item['handle'], '+{} : -{}'.format(
                item['successfulHackCount'], item['unsuccessfulHackCount']
            )]
        )
    print(standings.get_string(sortby='Rank'))
