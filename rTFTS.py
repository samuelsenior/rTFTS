import praw
import argparse
import sys
"""
    ToDo:
        -Add in documentation strings to functions and add comments so it's
        easier to follow code
        -Check the fetching of posts actually stops when args.num_posts is
        found rather than finding say 25 long and only displaying 10 for
        instance
            -maybe add in option to display the top say 15 but fetch the top 20
            or top 16 etc at a time?
                -But at the very least stop it searching for 25 epics when
                you only want one
        -Make an authors blacklist as well?
        -Make it display the top len(posts) rather than always top ten
        -Add in scrolling down to next n posts
        -Get_top can cause an error if the number of top posts in the last
        24 hours (for example) is less than the number of posts you're trying
        to fetch. (So it gets say 7 and then tries to call posts[8] which
        doesn't exist and gives a KeyError)
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 20:21:18 2016

@author: sms1n16
"""


def read_in_submissions(subreddit_name='TalesFromTechSupport',
                        sort='hot', time='', count=10, num_sub=25, after=''):
    if num_sub >= 100:
        pass
    elif num_sub > 25:
        num_sub = num_sub * 2
    else:
        num_sub = 25
    para = {}
    para['count'] = count  # Not sure if I need this, should probably check
    para['limit'] = num_sub  # Number of posts to fetch at a time
    para['after'] = after  # ID of last post fetched
    para['time'] = time  # The time over which to get posts from
    r = praw.Reddit('redditTFTS')
    if sort == 'hot':
        return r.get_subreddit(subreddit_name).get_hot(params=para)
    elif sort == 'new':
        return r.get_subreddit(subreddit_name).get_new(params=para)
    elif sort == 'rising':
        return r.get_subreddit(subreddit_name).get_rising(params=para)
    elif sort == 'controversial':
        return r.get_subreddit(subreddit_name).get_controversial(params=para)
    elif sort == 'top':
        return r.get_subreddit(subreddit_name).get_top(params=para)
    elif sort == 'gilded':
        return r.get_subreddit(subreddit_name).get_gilded(params=para)


def load_posts(s):
    submissions = read_in_submissions(num_sub=s, sort=args.sort)
    i = 1
    to_fetch = 0
    last = ''
    for submission in submissions:
        if blacklist(submission.title) is True:
            to_fetch = to_fetch + 1
        elif flaircheck(submission.link_flair_text) is False:
            to_fetch = to_fetch + 1
        else:
            posts[i] = (submission.id, submission.title, submission.selftext,
                        submission.author, submission.link_flair_text,
                        submission.permalink)
            i = i + 1
        last = submission.name
        if i > args.num_posts:
            break
    while to_fetch > 0:
        submissions = read_in_submissions(num_sub=s, after=last,
                                          sort=args.sort)
        for submission in submissions:
            if blacklist(submission.title) is True:
                last = submission.name
            elif flaircheck(submission.link_flair_text) is False:
                last = submission.name
            else:
                to_fetch = to_fetch - 1
                last = submission.name
                if to_fetch <= 0:
                    break
                posts[1 + len(posts)] = (submission.id,
                                         submission.title,
                                         submission.selftext,
                                         submission.author,
                                         submission.link_flair_text,
                                         submission.permalink)
    return posts


def blacklist(title):
    try:
        with open('blacklist.txt', 'rt') as f:
            for line in f.readlines():
                if line.split('\n')[0] == title:
                    return True
            return False
    except FileNotFoundError:
        return False


def flaircheck(flair):
    flair = flair.split(' ')[0].lower()  # To fix 'Short r/all' instances etc
    if args.flair == flair:
        return True
    elif isinstance(args.flair, type(None)):
        return True
    else:
        return False
    return True


def title():
    print("\n-------------------")
    print("       rTFTS")
    print("-------------------")
    print("Top ten posts:")


def print_top_ten(posts):
    for i in range(1, args.num_posts + 1):
        print("{}: ".format(i), end='')
        print_post(posts, s=i, title=2, author=2, flair=2)


def print_post(posts, s, id=0, title=0, selftext=0, author=0, flair=0):
    if id == 1:
        print(posts[s][0])
    if title == 1:
        print(posts[s][1])
    elif title == 2:
        print("{}".format(posts[s][1]), end='')
    if selftext == 1:
        print(posts[s][2])
    if author == 1:
        print(posts[s][3])
    elif author == 2:
        print(" - {} ".format(posts[s][3]), end='')
    if flair == 1:
        print(posts[s][4])
    elif flair == 2:
        print(" ({})".format((posts[s][4])))


def get_choice():
    action = input("\nSelect post ('0' for exit): ")
    if action.isnumeric():
        action = int(action)
        if action > 0 and action <= args.num_posts:
            print("\n--------------------------")
            print_post(posts, s=int(action), title=2, author=2, flair=2)
            print("--------------------------")
            print_post(posts, int(action), selftext=1)
        elif action == 0:
            print("Exiting...")
            sys.exit()
        elif action > args.num_posts:
            print("Error, choice entered greater than",
                  "the possible choices")

    elif((action.split()[0] == '-f' or action.split()[0] == '--flair')
         and persistance is True):
        choices = ['short', 'Short', 'medium', 'Medium', 'long', 'Long',
                   'epic', 'Epic', 'best', 'Best', 'BEST']
        if len(action.split()) == 1:
            print('Error, no flair given')
        elif choices.count(action.split()[1]) == 1:
            args.flair = action.split()[1]
            args.flair = args.flair.lower()
            print("{} {} {}".format('Flair of type', args.flair, 'set'))
        elif choices.count(action.split()[1]) == 0:
            print("{} {} {} {}".format('Error, undefined flair of',
                  action.split()[1], "given. \nPlease choose from types:",
                  "'Short', 'Medium', 'Long', 'Epic'."))

    elif((action.split()[0] == '-n' or action.split()[0] == '--num_posts')
         and persistance is True):
        if len(action.split()) == 1:
            print('Error, no number given')
        elif not action.split()[1].isnumeric():
            print('Error, non-numeric string given as arguemnt')
            print('Error, type int not given')
        else:
            args.num_posts = int(action.split()[1])

    elif((action.split()[0] == '-s' or action.split()[0] == '--sort')
         and persistance is True):
        choices = ['hot', 'new', 'rising', 'controversial', 'top', 'gilded']
        if len(action.split()) == 1:
            print('Error, no sorting method given')
        elif choices.count(action.split()[1]) == 1:
            args.sort = action.split()[1]
        elif choices.count(action.split()[1]) == 0:
            print("{} {} {} {}".format('Error, undefined sorting method of',
                  action.split()[1], "given. \nPlease choose from types:",
                  "'hot', 'new', 'rising' etc."))

    else:
        print("Error, choice is not numeric")


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--flair',
                        choices=['short', 'Short', 'medium', 'Medium',
                                 'long', 'Long', 'epic', 'Epic',
                                 'best', 'Best', 'BEST'],
                        required=False)
    parser.add_argument('-n', '--num_posts', type=int, default=10,
                        required=False)
    parser.add_argument('-s', '--sort',
                        choices=['hot', 'new', 'rising', 'controversial',
                                 'top', 'gilded'],
                        default='hot', required=False)
    parser.add_argument('-p', '--persistance', choices=['True', 'False'],
                        default=False, required=False)
    arguments = parser.parse_args()
    if arguments.flair is not None:
        arguments.flair = arguments.flair.lower()
    if isinstance(arguments.num_posts, int):
        arguments.num_posts = arguments.num_posts
    else:
        arguments.num_posts = 10
    if arguments.sort is not None:
        pass
    else:
        arguments.sort = ''
    if arguments.persistance == 'True':
        arguments.persistance = True
    elif arguments.persistance == 'False':
        arguments.persistance = False
    return arguments


args = get_arguments()
persistance = True
while persistance:
    if args.persistance is False:
        persistance = False
    title()
    posts = {}
    posts = load_posts(s=args.num_posts)
    print_top_ten(posts)
    get_choice()
    if args.persistance is True:
        input('< Press enter to continue > ')
