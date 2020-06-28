import os
from subprocess import Popen

from . import cf_login
from .cf_colors import Colors


def parse(group, contest, problem):
    Popen(['rm', '-rf', 'files']).wait()
    Popen(['mkdir', '-p', 'files']).wait()
    print('%sImporting samples of problem %s...%s' % (Colors.WARNING, str(contest + problem), Colors.END))
    j = 0
    try:
        browser = cf_login.login()
        if group is not None:
            url = 'https://codeforces.com/group/%s/contest/%s/problem/%s' % (group, contest, problem)
        elif len(str(contest)) >= 6:
            url = 'https://codeforces.com/gym/%s/problem/%s' % (contest, problem)
        else:
            url = 'https://codeforces.com/contest/%s/problem/%s' % (contest, problem)
        browser.open(url)
        page = browser.parsed
        sample_test = page.find('div', class_='sample-test')
        inputs = sample_test.find_all('div', class_='input')
        for i in inputs:
            input_text = i.find('pre')
            input_text = str(input_text).replace(
                '<br/>', '\n').replace('<pre>', '').replace('</pre>', '')
            create_file(input_text.strip(), 'test%d.in' % j)
            j += 1
        outputs = sample_test.find_all('div', class_='output')
        j = 0
        for i in outputs:
            output_text = i.find('pre')
            output_text = str(output_text).replace(
                '<br/>', '\n').replace('<pre>', '').replace('</pre>', '')
            create_file(output_text.strip(), 'test%d.ans' % j)
            j += 1
    except Exception:
        print('%sError, try in few minutes!!%s' % (Colors.FAIL, Colors.END))
        return
    print('%s%d samples imported successfully!%s' % (Colors.OK_GREEN, j, Colors.END))


def create_file(source, file_name):
    file = open(os.path.join('files', file_name), 'w')
    file.write(source)
    file.close()
