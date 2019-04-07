import sys
import re
import os
import argparse
import webbrowser

from . import cf_login
from . import cf_problems
from . import cf_contests
from . import cf_gyms
from . import cf_groups
from . import cf_standings
from . import cf_submit
from . import cf_hack
from . import cf_parse
from . import cf_test
from . import cf_io_utils
from .cf_colors import colors


# print standings

def print_standings(group, contest, verbose, top, sort, showall):
    # requires login
    browser = cf_login.login()
    if group is not None:
        # group contest contest
        url = "http://codeforces.com/group/" + \
            group + "/contest/" + contest + "/standings"
    elif len(str(contest)) >= 6:
        # gym contest
        url = "http://codeforces.com/gym/" + contest + "/standings"
    else:
        # codeforces round
        url = "http://codeforces.com/contest/" + contest + "/standings"
    # check if friends
    if group is not None:
        url += "/groupmates/true"
    elif showall is False:
        url += "/friends/true"
    else:
        url += "/page/1"
    browser.open(url)
    cf_standings.print_st(browser.parsed, verbose, top, sort)


# get time

def print_time(group, contest):
    browser = cf_login.login()
    if contest is None:
        print("Set contest first with: cf con/gym --id 1111")
        return
    if group is not None:
        url = "http://codeforces.com/group/" + group + "/contest/" + contest + "/submit"
    elif len(str(contest)) >= 6:
        url = "http://codeforces.com/gym/" + contest + "/submit"
    else:
        url = "http://codeforces.com/contest/" + contest + "/submit"
    browser.open(url)
    countdown_timer = browser.parsed.find_all(
        "span", class_="contest-state-regular countdown before-contest-" + contest + "-finish")
    if len(countdown_timer) == 0:
        print("Contest " + contest + " is over")
    else:
        print("%sTIME LEFT: %s%s" %
              (colors.BOLD, str(countdown_timer[0].get_text(strip=True)), colors.ENDC))


# main

def main():
    cache_loc = os.path.join(os.environ['HOME'], '.cache', 'cf_submit')
    if os.path.isdir(cache_loc) is False:
        os.mkdir(cache_loc)
    config_loc = os.path.join(cache_loc, "config.json")
    config = cf_io_utils.read_data_from_file(config_loc)
    if config is None:
        config = dict()
        cf_io_utils.write_data_in_file(config, config_loc)
    # ------------------- argparse --------------------
    parser = argparse.ArgumentParser(
        description="Command line tool to submit to codeforces", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("command", help="con/gym/gcon -- change contest or gym or group contest id\n" +
                                        "hack -- try to hack all the accepted submissions for a specific given problem\n" +
                                        "ext -- change default file extension\n" +
                                        "ext -- change default file extension\n" +
                                        "info -- current handle and contest id\n" +
                                        "login -- save login info\n" +
                                        "peek -- look at last submission\n" +
                                        "problems -- show number of solves on each problem\n" +
                                        "standings -- show standings of friends in default contest, or specify contest with -p\n" +
                                        "submit -- submit code to problem\n" +
                                        "time -- shows time left in contest\n" +
                                        "watch -- watch last submission\n" +
                                        "open -- open selected problem on default browser\n" +
                                        "parse -- import selected problem samples data\n" +
                                        "test -- test the selected source code with the imported tests data\n"
                        )
    parser.add_argument("option",
                        nargs='*', default=None,
                        help="file to submit"
                        )
    parser.add_argument("--handle",
                        action="store", default=None,
                        help="specify handle, example: --handle _bacali"
                        )
    parser.add_argument("--id",
                        action="store", default=None,
                        help="specify contest or gym id, example: --id 1117"
                        )
    parser.add_argument("-p", "--prob",
                        action="store", default=None,
                        help="specify problem, example: -p 845a"
                        )
    parser.add_argument("--pretty-off",
                        action="store_true", default=False,
                        help="turn pretty print off"
                        )
    parser.add_argument("-l", "--lang",
                        action="store", default=None,
                        help="specify language, example: -l cpp11"
                        )
    parser.add_argument("-c", "--contest",
                        action="store", default=None,
                        help="specify contest when getting standings"
                        )
    parser.add_argument("--group",
                        action="store", default=None,
                        help="specify group"
                        )
    parser.add_argument("-w", "--watch",
                        action="store_true", default=False,
                        help="watch submission status"
                        )
    parser.add_argument("-v", "--verbose",
                        action="store_true", default=False,
                        help="show more when looking at standings"
                        )
    parser.add_argument("-a", "--all",
                        action="store_true", default=False,
                        help="show common standings"
                        )
    parser.add_argument("-t", "--top",
                        type=int, nargs='?', const=10, default=50,
                        help="number of top contestants to print"
                        )
    parser.add_argument("-s", "--sort",
                        choices=["solves", "index", "id"],
                        type=str, nargs='?', const="solves", default=None,
                        help="sort by: solves (default), index (id)"
                        )
    parser.add_argument("-g", "--guru",
                        action="store_true", default=False,
                        help="submit to acmsguru problemset"
                        )
    parser.add_argument("-n", "--number",
                        type=int, action="store", default=10,
                        help="number of tests"
                        )

    args = parser.parse_args()

    # deal with short commands
    if args.command == "st":
        args.command = "standings"
    elif args.command == "pb":
        args.command = "problems"
    if args.sort == "id":
        args.sort = "index"

    # do stuff
    if args.command == "gcon":
        # set group contest
        # check if bad input
        if args.group is None:
            group = input("Group Id: ")
        else:
            group = args.group

        if args.contest is None:
            contest = input("Contest number: ")
        else:
            contest = args.contest
        config["contest"] = contest
        config["group"] = group
        cf_io_utils.write_data_in_file(config, config_loc)
        print("Group set to " + group)
        print("Contest set to " + contest)

    elif args.command == "gym" or args.command == "con":
        # set contest
        # check if bad input
        if args.id is not None:
            contest = args.id
        else:
            contest = input("Contest/Gym number: ")
        config["contest"] = contest
        config["group"] = None
        cf_io_utils.write_data_in_file(config, config_loc)
        if len(contest) >= 6:
            print("Gym set to " + contest)
        else:
            print("Contest set to " + contest)
    elif args.command == "groups":
        cf_groups.load_groups(args.pretty_off)
    elif args.command == "gcontests":
        if args.group is None:
            group = input("Group Id: ")
        else:
            group = args.group
        cf_groups.load_contests(group, args.pretty_off)
    elif args.command == "contests":
        cf_contests.load_contests(args.pretty_off)
    elif args.command == "gyms":
        cf_gyms.load_gyms(args.pretty_off)
    elif args.command == "ext":
        if len(args.option) > 1:
            print("Bad input")
            return
        if len(args.option) == 1:
            defext = args.option[0]
        else:
            defext = input("Default file extension: ")
        config["ext"] = defext
        cf_io_utils.write_data_in_file(config, config_loc)
        print("Default extension set to " + defext)

    elif args.command == "info":
        print("handle: " + str(config.get("handle", None)))
        print("groupID: " + str(config.get("group", None)))
        print("contestID: " + str(config.get("contest", None)))

    elif args.command == "login":
        # set login info
        if args.handle is None:
            cf_login.set_login()
        else:
            cf_login.set_login(args.handle)

    elif args.command == "peek":
        # look at last submission
        cf_submit.peek(config.get("handle", None))

    elif args.command == "watch":
        cf_submit.watch(config.get("handle", None))

    elif args.command == "time":
        print_time(args.group or config.get("group", None),
                   args.contest or config.get("contest", None))

    elif args.command == "standings":
        # look at standings
        print_standings(args.group or config.get("group", None),
                        args.contest or config.get("contest", None),
                        args.verbose, args.top, args.sort, args.all)

    elif args.command == "problems":
        # look at problem stats
        cf_problems.load_problems(args.pretty_off)

    elif args.command == "submit":
        # open browser
        browser = cf_login.login()
        if browser is not None:
            cf_submit.submit_files(
                browser, config.get("handle", None),
                args.group or config.get("group", None),
                args.contest or config.get("contest", None),
                args.prob,
                config.get("ext", None),
                args.lang, args.option, args.watch, args.guru
            )
    elif args.command == "test":
        if not os.path.isdir("files"):
            print("Please import problem testcases first by:\n\tcf parse -p a")
            return
        if len(args.option) == 0:
            print("Please select the source file")
            return
        cf_test.test(args.option[0], args.lang)
    elif args.command == "parse":
        if args.prob is None:
            problem = input("Problem Id: ")
        else:
            problem = args.prob
        if len(problem) < 3:
            cf_parse.parse(config.get("group", None),
                           config.get("contest", None),
                           str(problem).upper())
        else:
            splitted = re.split(r"(\D+)", problem)
            cf_parse.parse(config.get("group", None), splitted[0], str(
                splitted[1]+splitted[2]).upper())
    elif args.command == "open":
        if args.prob is None:
            print("Please select problem to open!!")
            return
        if config.get("group", None) is None:
            if len(args.prob) < 3:
                webbrowser.open("https://codeforces.com/contest/%s/problem/%s"
                                % (config.get("contest", None), str(args.prob).upper()), 2)
            else:
                splitted = re.split(r"(\D+)", args.prob)
                webbrowser.open("https://codeforces.com/contest/%s/problem/%s"
                                % (splitted[0], str(splitted[1]+splitted[2]).upper()), 2)
        else:
            if len(args.prob) < 3:
                webbrowser.open("https://codeforces.com/group/%s/contest/%s/problem/%s"
                                % (config.get("group", None), config.get("contest", None),
                                   str(args.prob).upper()), 2)
            else:
                splitted = re.split(r"(\D+)", args.prob)
                webbrowser.open("https://codeforces.com/group/%s/contest/%s/problem/%s"
                                % (config.get("contest", None), splitted[0],
                                   str(splitted[1]+splitted[2]).upper()), 2)
    elif args.command == "hack":
        if len(args.option) < 3:
            print(
                "Please select your <generator-source> [<tle-generator-source>] <checker-source> <answer-source> !!")
            return
        if args.prob is None:
            print("Please select problem to try!!")
            return

        if len(args.option) == 3:
            cf_hack.begin_hack(config.get("contest", None), args.prob, args.option[0], None,
                               args.option[1], args.option[2], args.number)
        else:
            cf_hack.begin_hack(config.get("contest", None), args.prob, args.option[0], args.option[1],
                               args.option[2], args.option[3], args.number)
    else:
        print("UNKNOWN COMMAND")


# END
