#! /usr/bin/env python3
import praw
import os
import time
import datetime
import secrets
from praw.exceptions import APIException

DEBUG = False

if DEBUG:
    SUB = "testingground4bots"
else:
    SUB = "rant+personalfinance+personalfinancecanada+truereddit+politics+news+worldnews+advice+relationships+finance+askreddit+funny"

MESSAGE_TEMPLATE = """/u/Paidpayedbot to the rescue! \n 
***** \n 
**Paid** or **payed** is the past tense of 'to pay' depending on the implied meaning of 'pay'. 
The first sense is the usual one of giving someone money while the second sense is to seal 
(the deck or seams of a wooden ship) with pitch or tar to prevent leakage.
You should almost always use **paid**, not **payed**.
***** \n
"""

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

def run_grammarbot(reddit):
    while(True):
        for comment in reddit.subreddit(SUB).comments(limit = 100000):
            if "payed" in comment.body:
                if comment.id not in posts_replied:
                    try:
                        comment.reply(MESSAGE_TEMPLATE)
                        print("Replied: ", comment.id)
                    except APIException:
                        with open("auto_smbc_bot.log","a") as f:
                            f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) + ": Rate Limit exception.\n")
                    except Exception:
                        print("General exception caught.")
                    if DEBUG:
                        print("Replied to: ", comment.id)
                    posts_replied.append(comment.id)
                    with open("replied_to.txt", "a") as f:
                        f.write(comment.id + "\n")
                if DEBUG:
                    print("Comment found: ", comment.id)
        time.sleep(900)

def main():
    reddit = authenticate()
    while True:
        run_grammarbot(reddit)

if __name__ == "__main__":
    main()