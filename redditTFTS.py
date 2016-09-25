import praw
import argparse
"""
    ToDo:
        -Add in documentation strings to functions
        -Check the fetching of posts actually stops when tot_posts is found
        rather than finding say 25 long and only displaying 10 for instance
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
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 20:21:18 2016

@author: sms1n16
"""


def read_in_submissions(url='https://www.reddit.com/r/talesfromtechsupport',
                        count=10, num_sub=25, after=''):
    if num_sub >= 1000:
        pass
    elif num_sub > 25:
        num_sub = num_sub * 2
    else:
        num_sub = 25
    para = {}
    para['count'] = count  # Not sure if I need this, should probably check
    para['limit'] = num_sub
    para['after'] = after
    r = praw.Reddit('redditTFTS')
    return r.get_content(url, params=para)


def load_posts(s):
    submissions = read_in_submissions(num_sub=s)
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
        submissions = read_in_submissions(num_sub=s, after=last)
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
        print('Error, blacklist.txt not found. Assumming no blacklist...')
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
    parser.add_argument('-n', '--num_posts', type=int, required=False)
    args = parser.parse_args()
    if args.flair is not None:
        args.flair = args.flair.lower()
    return args


args = get_arguments()
if isinstance(args.num_posts, int):
    tot_posts = args.num_posts
else:
    tot_posts = 10
title()
posts = {}
posts = load_posts(tot_posts)
print_top_ten(posts)
get_choice(tot_posts)
