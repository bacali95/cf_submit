import re
import sys
import time

from .cf_colors import Colors
from .cf_utils import safe_list_get
from .codeforces import CodeforcesAPI

codeforces = CodeforcesAPI()


# submissions
def get_submission_data(handle):
    submission = safe_list_get(codeforces.userSubmissions(handle, count=1), 0)
    if submission is None:
        print('Connection Error!')
    # check if verdict exists (in queue if not)
    if not hasattr(submission, 'verdict'):
        setattr(submission, 'verdict', 'IN QUEUE')
    return submission


# look at last submission
def peek(handle):
    submission = get_submission_data(handle)
    if not hasattr(submission.problem, 'contestId'):
        setattr(submission.problem, 'contestId', 'guru')
    problem = '%s%s' % (submission.problem.contestId, submission.problem.index)
    if submission.verdict == 'TESTING':
        print('Submission %s to problem %s: %s'
              % (submission.id, problem, submission.verdict))
    else:
        if submission.verdict != 'OK':
            print('Submission %s to problem %s: %s on test %s\nTime:   %sms \nMemory: %sKb'
                  % (submission.id, problem, submission.verdict, 1 + submission.passedTestCount,
                     submission.timeConsumedMillis, submission.memoryConsumedBytes / 1024))
        else:
            print('Submission %s to problem %s: %s! passed all %s tests\nTime:   %sms \nMemory: %sKb'
                  % (submission.id, problem, submission.verdict, submission.passedTestCount,
                     submission.timeConsumedMillis, submission.memoryConsumedBytes / 1024))


# watch last submission
def watch(handle):
    spinner = {0: '◴', 1: '◵', 2: '◶', 3: '◷'}
    count = 0
    while True:
        submission = get_submission_data(handle)
        if not hasattr(submission.problem, 'contestId'):
            setattr(submission.problem, 'contestId', 'guru')
        problem = '%s%s' % (submission.problem.contestId,
                            submission.problem.index)
        if submission.verdict not in ['TESTING', 'IN QUEUE']:
            if submission.verdict != 'OK':
                sys.stdout.write('\rSubmission %s to problem %s: %s on test %s\nTime:   %sms \nMemory: %sKb'
                                 % (submission.id, problem, submission.verdict, 1 + submission.passedTestCount,
                                    submission.timeConsumedMillis, submission.memoryConsumedBytes / 1024))
            else:
                sys.stdout.write('\rSubmission %s to problem %s: %s! passed all %s tests\nTime:   %sms \nMemory: %sKb'
                                 % (submission.id, problem, submission.verdict, submission.passedTestCount,
                                    submission.timeConsumedMillis, submission.memoryConsumedBytes / 1024))
            sys.stdout.flush()
            break
        else:
            sys.stdout.write('\rSubmission %s to problem %s: %s ....... %s    '
                             % (submission.id, problem, submission.verdict, spinner[count]))
            sys.stdout.flush()
            count = (count + 1) % 4
        time.sleep(0.25)
    print('\a')


# submit problem

def submit_problem(browser, contest, lang, source, guru):
    # get form
    submission = browser.get_form(class_='submit-form')
    if submission is None:
        print('Cannot find problem')
        return False

    # submit form
    submission['sourceFile'] = source
    if lang == 'cpp':
        # GNU G++14 6.2.0
        lang_code = '50'
        # GNU G++11 5.1.0
        # lang_code = '42'
    elif lang == 'c':
        # GNU GCC C11 5.1.0
        lang_code = '43'
    elif lang == 'd':
        lang_code = '28'
    elif lang == 'py':
        # python 2.7.12
        # lang_code = '7'
        # python 3.5.2
        lang_code = '31'
    elif lang == 'rb':
        # Ruby 2.0.0p645
        lang_code = '8'
    elif lang == 'kt':
        lang_code = '48'
    elif lang == 'java':
        # Java 1.8.0_112
        lang_code = '36'
    elif lang == 'scala':
        lang_code = '20'
    elif lang == 'rs':
        lang_code = '49'
    elif lang == 'php':
        lang_code = '6'
    else:
        print('Unknown Language')
        return False
    submission['programTypeId'] = lang_code

    # check acmsguru
    if guru != -1:
        submission['submittedProblemCode'] = guru

    browser.submit_form(submission)

    # check if good
    if (guru != -1 and browser.url[-7:] != '/status') or (guru == -1 and browser.url[-3:] != '/my'):
        print('Failed to submit code')
        print(' @ %s' % (str(browser.url)))
        return False
    print('Code submitted properly')

    # now get time
    countdown_timer = browser.parsed.find_all(
        'span', class_='contest-state-regular countdown before-contest-' + contest + '-finish')
    if len(countdown_timer) > 0:
        print('%sTIME LEFT: %s%s' % (Colors.BOLD, str(countdown_timer[0].get_text(strip=True)), Colors.END))

    return True


# submit problem
def submit(browser, handle, group, contest, problem, lang, source, show, guru):
    if guru:
        print('Submitting to acmsguru %s as %s'
              % (problem, handle))
    elif group is not None:
        print('Submitting to problem %s%s in group %s as %s'
              % (contest, problem.upper(), group, handle))
    else:
        print('Submitting to problem %s%s as %s'
              % (contest, problem.upper(), handle))

    pid = -1
    if guru:
        browser.open('http://codeforces.com/problemsets/acmsguru/submit')
        pid = problem
    elif group is not None:
        browser.open('http://codeforces.com/group/%s/contest/%s/submit/%s'
                     % (group, contest, problem.upper()))
    elif len(contest) >= 6:
        browser.open('http://codeforces.com/gym/%s/submit/%s'
                     % (contest, problem.upper()))
    else:
        browser.open('http://codeforces.com/contest/%s/submit/%s'
                     % (contest, problem.upper()))

    # show submission
    if submit_problem(browser, contest, lang, source, pid) and show:
        watch(handle)


# submit, possibly len(args) > 1
def submit_files(browser, default_handle, default_group, default_contest, default_prob, def_ext, default_lang,
                 args, show, guru):
    # if len == 0, query for file
    if len(args) == 0:
        args.append(input('File to submit: '))

    for source in args:
        # split file name
        info = source.split('.')
        # single filename
        if source.find('.') == -1:
            info.append(def_ext)
            source += '.' + def_ext

        # check language
        if default_lang is not None:
            info[-1] = default_lang

        # submit problem
        if default_prob is not None:
            if len(default_prob) == 1:
                # letter only
                submit(browser, default_handle, default_group, default_contest,
                       default_prob, info[-1], source, show, guru)
            elif len(default_prob) == 2:
                # letter + number (?)
                submit(browser, default_handle, default_group, default_contest,
                       default_prob, info[-1], source, show, guru)
            else:
                #  parse string
                split = re.split(r'(\D+)', default_prob)
                if len(split) == 3 and len(split[1]) == 1 and len(split[2]) == 0:
                    # probably a good string
                    submit(browser, default_handle, default_group,
                           split[0], split[1], info[-1], source, show, guru)
                else:
                    print('cannot understand the problem specified')

        elif len(info) == 2:
            if guru:
                # ACMSGURU
                submit(browser, default_handle, default_group,
                       default_contest, info[0], info[1], source, show, guru)
            else:
                # CODEFORCES
                # try to parse info[0]
                if info[0][:2].lower() == 'cf':
                    # remove the cf
                    info[0] = info[0][2:]
                if len(info[0]) == 1:
                    # only the letter, use default contest
                    submit(browser, default_handle, default_group,
                           default_contest, info[0], info[1], source, show, guru)
                else:
                    # contest is included, so parse
                    split = re.split(r'(\D+)', info[0])
                    if len(split) == 3 and len(split[1]) == 1 and len(split[2]) == 0:
                        # probably good string ?
                        submit(browser, default_handle, default_group,
                               split[0], split[1], info[1], source, show, guru)
                    else:
                        print(
                            'cannot parse filename, specify problem with -p or --prob')
        else:
            print('cannot parse filename, specify problem with -p or --prob')
