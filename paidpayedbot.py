#! /usr/bin/env python3
import praw
import os
import time
import datetime
import secrets
from praw.exceptions import APIException

# Flag True to debug in testing subreddit
DEBUG = False

if DEBUG:
    SUB = "testingground4bots"
else:
    SUB = "all"

# Message used in comment reply
MESSAGE_TEMPLATE = """/u/Paidpayedbot found a common grammar mistake in your comment. \n 
***** \n 
**Paid** or **payed** is the past tense of 'to pay' depending on the implied meaning of 'pay'. 
The first form is the common meaning of giving someone money while the second form is to seal 
(the deck or seams of a wooden ship) with pitch or tar to prevent leakage.\n
You should almost always use **paid**, not **payed**.
***** \n
"""

# Authenticate with Reddit
def authenticate():
    print("Authenticating...\n")
    reddit = praw.Reddit("paidpayed", user_agent="paidpayedbot:v0.1")
    print("Authenticated as {}\n".format(reddit.user.me()))
    return reddit

if not os.path.isfile("replied_to.txt"):
    posts_replied = []
else:
    with open("replied_to.txt", "r") as f:
        posts_replied = f.read()
        posts_replied = posts_replied.split("\n")
        posts_replied = list(filter(None, posts_replied))

# Terms
my_keywords = [' payed']

# Function which searches through comment across all subreddits looking for specific grammar mistake
def run_grammarbot(reddit):
    while(True):
        for comment in reddit.subreddit(SUB).stream.comments():
            if any(keyword in comment.body for keyword in my_keywords):
                if comment.id not in posts_replied:
                    if comment.author.name != "paidpayedbot":
                        try:
                            comment.reply(MESSAGE_TEMPLATE)
                            print("Replied to ", comment.id, " written by ", comment.author.name)
                        except APIException:
                            with open("auto_smbc_bot.log","a") as f:
                                f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) + ": Rate Limit exception.\n")
                                time.sleep(600) # Equals ten minutes, roughly equal to Rate Limit 
                        except Exception as e:
                            print("General exception caught: ", e)
                            time.sleep(60)
                        if DEBUG:
                            print("Replied to: ", comment.id)
                        posts_replied.append(comment.id)
                        with open("replied_to.txt", "a") as f:
                            f.write(comment.id + "\n")
                    if DEBUG:
                        print("Comment found: ", comment.id)
                    time.sleep(30)
# Run while authenticated
def main():
    reddit = authenticate()
    while True:
        run_grammarbot(reddit)

if __name__ == "__main__":
    main()