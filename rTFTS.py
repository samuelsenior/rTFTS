import praw
import argparse
"""
    ToDo:
        -Add in documentation strings to functions and add comments so it's
        easier to follow code
        -Check the fetching of posts actually stops when tot_posts is found
        rather than finding say 25 long and only displaying 10 for instance
            -maybe add in option to display the top say 15 but fetch the top 20
            or top 16 etc at a time?
                -But at the very least stop it searching for 25 epics when
                you only want one
        -Make an authors blacklist as well?
        -Flair filter
            -extend to persistant menu
        -Make it display the top len(posts) rather than always top ten
        -Add in scrolling down to next n posts
        -Add in menu persistance option
            -e.g. called with tfts -p
            -pause after reading post and then enter takes it back to the main
            menu
        -Pause it so need to press enter to finish reading post
            -only if menu loop is enabled
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
        if i > tot_posts:
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
    print("\n------------------")
    print("    RedditTFTS")
    print("------------------")
    print("Top ten posts:")


def print_top_ten(posts):
    for i in range(1, tot_posts + 1):
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


def get_choice(tot_posts):
    action = input("\nSelect post ('0' for exit): ")
    if action.isnumeric():
        action = int(action)
        if action > 0 and action <= tot_posts:
            print("\n--------------------------")
            print_post(posts, s=int(action), title=2, author=2, flair=2)
            print("--------------------------")
            print_post(posts, int(action), selftext=1)
        elif action == 0:
            print("Exiting...")
            exit
        elif action > tot_posts:
            print("Error, choice entered greater than",
                  "the possible choices. Exiting...")
    else:
        print("Error, choice is not numeric. Exiting...")
        exit


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
    return arguments


args = get_arguments()
tot_posts = args.num_posts
title()
posts = {}
posts = load_posts(tot_posts)
print_top_ten(posts)
get_choice(tot_posts)
