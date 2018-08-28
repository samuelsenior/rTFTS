import praw
import argparse
import sys

class TFTS():

    def __init__(self):
        self._persistance = True
        self._args = None
        self._get_arguments()
        self._para = None
        self._posts = {}
        self._submissions = None
        self.main()

    def _get_arguments(self):
        """Gets arguments passed in from terminal when rTFTS is called."""
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--flair',
                            choices=['short', 'Short', 'medium', 'Medium',
                                     'long',  'Long',  'epic',   'Epic',
                                     'best',  'Best',  'BEST'],
                            required=False)  # Flair argument
        parser.add_argument('-n', '--num_posts', type=int, default=10,
                            required=False)  # Number of posts to display argument
        parser.add_argument('-s', '--sort',
                            choices=['hot', 'new', 'rising', 'controversial',
                                     'top'], default='hot',
                            required=False)  # Sorting method argument,
        # 'gilded' currently removed as it's broken
        parser.add_argument('-p', '--persistance', choices=['True',  'true',
                                                            'False', 'false'],
                            default='false',
                            required=False)  # Menu persistance argument

        self._args = parser.parse_args()
        if self._args.flair is not None:  # Check a flair has an argument
            self._args.flair = self._args.flair.lower()
        if isinstance(self._args.num_posts, int):  # Check number of posts is an int
            self._args.num_posts = self._args.num_posts  # Not sure here
        else:
            self._args.num_posts = 10  # If not, give a defualt value
        if self._args.sort is not None:  # Check sort is defined
            pass
        else:  # If not, give it an empty string
            self._args.sort = ''
        self._args.persistance = self._args.persistance.lower()
        if self._args.persistance == 'true':  # Set the strings to equiv bools
            self._args.persistance = True
        elif self._args.persistance == 'false':
            self._args.persistance = False

    def _read_in_submissions(self, subreddit_name='TalesFromTechSupport',
                             sort='hot', time='', count=10, num_sub=25, after=''):
        """Reads in the subreddit and posts based upone the arguments passed to
        it and returns a praw.reddit()"""
        if num_sub >= 100:
            pass
        elif num_sub > 25:
            num_sub = num_sub * 2
        else:
            num_sub = 25
        self._para = {}
        self._para['count'] = count  # Not sure if I need this, should probably check
        self._para['limit'] = num_sub  # Number of posts to fetch at a time
        self._para['after'] = after  # ID of last post fetched
        self._para['time'] = time  # The time over which to get posts from
        reddit = praw.Reddit(client_id='ZqwhW0ovrIEkhQ',
                             client_secret=None,
                             redirect_uri='http://localhost:8080',
                             user_agent='python:rTFTS:0.1.0 (by /u/rTFTS_bot)')
        subreddit = reddit.subreddit(subreddit_name)
        if sort == 'hot':
            self._submissions = subreddit.hot(params=self._para)
        elif sort == 'new':
            self._submissions = subreddit.new(params=self._para)
        elif sort == 'rising':
            self._submissions = subreddit.rising(params=self._para)
        elif sort == 'controversial':
            self._submissions = subreddit.controversial(params=self._para)
        elif sort == 'top':
            self._submissions = subreddit.top(params=self._para)
        # elif sort == 'gilded':
        #    return subreddit.gilded(params=para)  # Currently broken

    def _blacklist(self, title):
        """If a post title is in the file 'blacklist.txt' then blacklist returns
        True and the post is excluded. Note, one post title per line."""
        try:
            with open('blacklist.txt', 'rt') as f:
                for line in f.readlines():
                    if line.split('\n')[0] == title:
                        return True
                return False
        except FileNotFoundError:
            return False

    def _flaircheck(self, flair):
        """Checks that the flair passed to flaircheck is the same as args.flair,
        returns True is that's the case."""
        flair = flair.split(' ')[0].lower()  # To fix 'Short r/all' instances etc
        if self._args.flair == flair:
            return True
        elif isinstance(self._args.flair, type(None)):
            return True
        else:
            return False
        return True

    def _load_posts(self, s):
        """Takes the read in praw.reddit() and returns a dictionary of posts
        based upon the posts that meet the criteria of the arguments passed to
        it."""
        self._read_in_submissions(num_sub=s, sort=self._args.sort)
        i = 1
        to_fetch = 0
        last = ''

        #for submission in self._submissions:
        count = 0
        self._submissions.next()  # Not sure why this is needed, but it stops an error...
        while i < self._submissions.limit:
            submission = self._submissions.next()
            count += 1
            # If blacklist() returns True add 1 to counter and don't get the post
            if self._blacklist(submission.title) is True:
                to_fetch = to_fetch + 1
            # If flaircheck returns False add 1 to counter and don't get the post
            elif self._flaircheck(submission.link_flair_text) is False:
                to_fetch = to_fetch + 1
            else:
                self._posts[i] = (submission.id, submission.title, submission.selftext,
                                  submission.author, submission.link_flair_text,
                                  submission.permalink)
                i = i + 1
            self._last = submission.name  # Keep track of the last posts ID for reference
            # Stop if the number of desired posts has been fetched (minus to_fetch)
            if i > self._args.num_posts:
                break
        # Fetch the number of posts that didn't mee thte criteria
        while to_fetch > 0:
            self._submissions = self._read_in_submissions(num_sub=s, after=self._last,
                                                          sort=self._args.sort)
            for submission in self._submissions:
                if self._blacklist(submission.title) is True:
                    last = submission.name
                elif self._flaircheck(submission.link_flair_text) is False:
                    last = submission.name
                else:
                    to_fetch = to_fetch - 1
                    self._last = submission.name
                    if to_fetch <= 0:
                        break
                    self._posts[1 + len(self._posts)] = (submission.id,
                                                         submission.title,
                                                         submission.selftext,
                                                         submission.author,
                                                         submission.link_flair_text,
                                                         submission.permalink)

    def _title(self):
        """Prints a basic title."""
        print("\n-------------------")
        print("       rTFTS")
        print("-------------------")
        print("Top ten posts:")  # Remove this at some point and put elsewhere

    def _print_post(self, posts, s, id=0, title=0, selftext=0, author=0, flair=0):
        """Prints post title, author, selftext, and flair depending on which
        arguments are passed to it"""
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

    def _print_top_ten(self, posts):
        """Prints the post title, author, and fliar on a single line."""
        for i in range(1, self._args.num_posts + 1):
            print("{}: ".format(i), end='')
            self._print_post(posts, s=i, title=2, author=2, flair=2)

    def _get_choice(self):
        """Gets the user choice for selecting a post to read or passing a value to
        an angrument if persistant menu is enabled."""
        action = input("\nSelect post ('0' for exit): ")
        act = action.split()[0]
        if action.isnumeric():
            action = int(action)
            if action > 0 and action <= self._args.num_posts:
                print("\n--------------------------")
                self._print_post(self._posts, s=int(action), title=2, author=2, flair=2)
                print("--------------------------")
                self._print_post(self._posts, int(action), selftext=1)
            elif action == 0:
                print("Exiting...")
                sys.exit()
            elif action > self._args.num_posts:
                print("Error, choice entered greater than",
                      "the possible choices")

        # Section for taking arguments
        # Flair argument
        elif((act == '-f' or act == '--flair') and self._persistance is True):
            choices = ['short', 'Short', 'medium', 'Medium', 'long', 'Long',
                       'epic', 'Epic', 'best', 'Best', 'BEST']
            # If no flair is given
            if len(action.split()) == 1:
                print('Error, no flair given')
            # The flair is the second item in the list
            elif choices.count(action.split()[1]) == 1:
                self._args.flair = action.split()[1]
                self._args.flair = self._args.flair.lower()
                print("{} {} {}".format('Flair of type', self._args.flair, 'set'))
            # If inputted flair not in the choices list
            elif choices.count(action.split()[1]) == 0:
                print("{} {} {} {}".format('Error, undefined flair of',
                      action.split()[1], "given. \nPlease choose from types:",
                      "'Short', 'Medium', 'Long', 'Epic'."))

        # Nuber of posts argument
        elif((act == '-n' or act == '--num_posts') and self._persistance is True):
            # If no number is given
            if len(action.split()) == 1:
                print('Error, no number given')
            # If the input is not an integer
            elif not action.split()[1].isnumeric():
                print('Error, non-integer string given as arguemnt')
            # Number of posts is the second item in the list
            else:
                self._args.num_posts = int(action.split()[1])

        # Sorting method argument
        elif((act == '-s' or act == '--sort') and self._persistance is True):
            choices = ['hot', 'new', 'rising', 'controversial', 'top', 'gilded']
            # If no sorting method is given
            if len(action.split()) == 1:
                print('Error, no sorting method given')
            # Sorting method is second item in the list
            elif choices.count(action.split()[1]) == 1:
                self._args.sort = action.split()[1]
            # If inputted sorting method is not in the list
            elif choices.count(action.split()[1]) == 0:
                print("{} {} {} {}".format('Error, undefined sorting method of',
                      action.split()[1], "given. \nPlease choose from types:",
                      "'hot', 'new', 'rising' etc."))

        # If the input doesn't correspond with a post number or argument
        else:
            print("Error, choice is not numeric")

    def main(self):
        self._persistance = True
        while self._persistance:
            if self._args.persistance is False:
                self._persistance = False
            self._title()
        self._load_posts(s=self._args.num_posts)
        self._print_top_ten(self._posts)
        self._get_choice()
        if self._args.persistance is True:
            input('< Press enter to continue > ')

tfts = TFTS()