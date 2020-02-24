#! /usr/bin/env python3
import praw
import os
import sys
import time
import datetime
import secrets
from praw.exceptions import APIException
from praw.models import Comment, Message, ModmailMessage

# Set flag to True to debug in testing subreddit
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
^Reply ^with ^'delete' ^with ^no ^single ^quotes ^if ^you ^wish ^for ^bot ^to ^remove ^comment
"""

GOOD_BOT = ":)"

BAD_BOT = "\r>:-("

# Authenticate with Reddit
def authenticate():
    print("\nAuthenticating...\n")
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

# Keyword array - separate terms with commas
my_keywords = [' payed']

# Received comments and messages arrays
unread_comments = []
unread_messages = []
unread_modmessages = []

# Main function
def run_grammarbot(reddit):
    print("Searching for keyword in comment stream...")

    # Scrapes comments from all subreddits    
    for comment in reddit.subreddit(SUB).stream.comments():
        time.sleep(3)
        if any(keyword in comment.body for keyword in my_keywords):
            if comment.id not in posts_replied:
                if comment.author.name != reddit.user.me:
                    try:
                        comment.reply(MESSAGE_TEMPLATE)
                        print("Replied to", comment.id, "written by", comment.author.name, "in", SUB)
                    except APIException:
                        with open("auto_smbc_bot.log","a") as f:
                            f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) + ": Rate Limit exception.\n")
                            time.sleep(600) # Equals ten minutes, roughly equal to Rate Limit
                            run_grammarbot(reddit)
                    except Exception as e:
                        print("General exception caught: ", e)
                        run_grammarbot(reddit)
                    if DEBUG:
                        print("Replied to: ", comment.id)
                    posts_replied.append(comment.id)
                    with open("replied_to.txt", "a") as f:
                        f.write(comment.id + "\n")
                if DEBUG:
                    print("Comment found: ", comment.id)
                time.sleep(30)

        # This loop searches inbox      
        for reply in reddit.inbox.unread(limit=None):
            time.sleep(3)
            try:
                print("Reply received...")

                # Handles three types of replies: messages, modmail and comments -- only responds to comments
                if isinstance(reply, Message):
                    print(reply.author.name, "has replied with a private message")
                    unread_messages.append(reply)
                    reddit.inbox.mark_read(unread_messages)
                    run_grammarbot(reddit)

                if isinstance(reply, ModmailMessage):
                    print(reply.author.name, "has replied with a moderator message")
                    unread_modmessages.append(reply)
                    reddit.inbox.mark_read(unread_modmessages)
                    run_grammarbot(reddit)

                if isinstance(reply, Comment):
                    if reply.id not in posts_replied:
                        print(reply.author.name, "has replied with:", reply.body)
                        posts_replied.append(reply.id)
                        unread_comments.append(reply)
                        reddit.inbox.mark_read(unread_comments)
                        with open("replied_to.txt", "a") as f:
                            f.write(reply.id + "\n")

                        if reply.body.lower() == 'delete':
                            parent = reply.parent()  # the comment made by your bot
                            parent.delete()
                            print("Comment deleted upon request by", reply.author.name)
                            run_grammarbot(reddit)
                        if reply.body.lower() == 'good bot':
                            reply.reply(GOOD_BOT)
                            print("Bot has replied with", GOOD_BOT)
                            run_grammarbot(reddit)        
                        if reply.body.lower() == 'bad bot':
                            reply.reply(BAD_BOT)
                            print("Bot has replied with", BAD_BOT)
                            run_grammarbot(reddit)
                        else:
                            run_grammarbot(reddit)
                    else:
                        break

            except APIException:
                with open("auto_smbc_bot.log","a") as f:
                    f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) + ": Rate Limit exception.\n")
                    run_grammarbot(reddit)

# Run while authenticated
def main():
    reddit = authenticate()
    while True:
        try:
            run_grammarbot(reddit)
        except Exception as e:
            print("General exception caught: ", e)
            run_grammarbot(reddit)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nQuit due to keyboard interruption')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)