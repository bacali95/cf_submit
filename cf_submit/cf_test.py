import glob
import os
from subprocess import Popen

from .cf_colors import Colors


def test(source, lang):
    info = source.split('.')
    if lang is None:
        lang = info[-1]
    if lang == 'py':
        print('%sPlease specify the version of python : py2 or py3%s' % (Colors.FAIL, Colors.END))
        return
    print('%sCompiling your %s solution...' % (Colors.OK_BLUE, lang))
    comp(source, lang, info[0])

    print('Executing...%s' % Colors.END)
    i = 1
    success = 0
    failed = 0
    for file_name in glob.iglob('files/test*.in'):
        with open(file_name, 'r') as input_file:
            with open(file_name.replace('.in', '.out'), 'w') as output_file:
                print('%s#################### TEST %d ####################%s\n' % (Colors.WARNING, i, Colors.END))
                i += 1
                execute(source, lang, info[0], input_file, output_file)
                process = Popen(['%s/bin/cf_checker' % os.path.dirname(os.path.abspath(__file__)),
                                 file_name, file_name.replace('.in', '.out'), file_name.replace('.in', '.ans')])
                process.wait(timeout=5)
                exit_code = process.returncode
                print('\n%sInput:%s' % (Colors.OK_BLUE, Colors.END))
                print(open(file_name, 'r').read(), '\n')
                if exit_code == 0:
                    success += 1
                else:
                    print('%sExpected:%s' % (Colors.OK_BLUE, Colors.END))
                    print(
                        str(open(file_name.replace('.in', '.ans'), 'r').read()).strip(), '\n')
                    failed += 1
                print('%sOutput:%s' % (Colors.OK_BLUE, Colors.END))
                print(
                    str(open(file_name.replace('.in', '.out'), 'r').read()).strip(), '\n')

    print('%s################################################%s\n' % (Colors.WARNING, Colors.END))
    print('%sSuccess: %d, %sFailed: %d%s' % (Colors.OK_GREEN, success, Colors.FAIL, failed, Colors.END))


def execute(source, lang, executable, input_file, output_file):
    if lang == 'cpp' or lang == 'c':
        cmd = './%s' % executable
    elif lang == 'java':
        cmd = 'java -DLOCAL %s' % executable
    elif lang == 'kt':
        cmd = 'java -DLOCAL -jar %s.jar' % executable
    elif lang == 'py2':
        cmd = 'python2 %s ' % source
    elif lang == 'py3':
        cmd = 'python3 %s ' % source
    else:
        print('Sorry language not supported!')
        return exit(-1)
    Popen(cmd, stdin=input_file, stdout=output_file, shell=True).wait()


def comp(source, lang, executable):
    if lang == 'cpp':
        cmd = 'g++ %s -DLOCAL -O2 -o %s' % (source, executable)
    elif lang == 'c':
        cmd = 'gcc %s -DLOCAL -O2 -o %s' % (source, executable)
    elif lang == 'java':
        cmd = 'javac %s' % source
    elif lang == 'kt':
        cmd = 'javac %s -include-runtime -d %s' % (source, executable)
    else:
        cmd = []
    Popen(cmd, shell=True).wait()
