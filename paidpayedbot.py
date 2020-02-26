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
    SUB = "personalfinancecanada+canada+onguardforthee+ontario+askacanadian+kpop+rant"

# Message used in comment reply
PAYED = """/u/Paidpayedbot found a common spelling mistake in your comment.\n 
***** \n 
**Paid** or **payed** is the past tense of 'to pay' depending on the implied meaning of 'pay'. 
The first form is the common meaning of giving someone money while the second form is to seal 
(the deck or seams of a wooden ship) with pitch or tar to prevent leakage.\n
You should almost always use **paid**, not **payed**.
***** \n
^Reply ^with ^'delete' ^\(with ^no ^single ^quotes\) ^if ^you ^wish ^for ^bot ^to ^remove ^comment
"""
DEFINATELY = """/u/Paidpayedbot found a common spelling mistake in your comment. \n 
***** \n 
**Definately** is spelled **definitely**.
***** \n
^Reply ^with ^'delete' ^\(with ^no ^single ^quotes\) ^if ^you ^wish ^for ^bot ^to ^remove ^comment
"""
NECCESSARY = """/u/Paidpayedbot found a common spelling mistake in your comment. \n 
***** \n 
**Neccessary** is spelled **necessary**.
***** \n
^Reply ^with ^'delete' ^\(with ^no ^single ^quotes\) ^if ^you ^wish ^for ^bot ^to ^remove ^comment
"""
OCCURED = """/u/Paidpayedbot found a common spelling mistake in your comment. \n 
***** \n 
**Occured** is spelled **occurred**.
***** \n
^Reply ^with ^'delete' ^\(with ^no ^single ^quotes\) ^if ^you ^wish ^for ^bot ^to ^remove ^comment
"""
SEPERATE = """/u/Paidpayedbot found a common spelling mistake in your comment. \n 
***** \n 
**Seperate** is spelled **separate**.
***** \n
^Reply ^with ^'delete' ^\(with ^no ^single ^quotes\) ^if ^you ^wish ^for ^bot ^to ^remove ^comment
"""

GOOD_BOT = ":)"

BAD_BOT = "\\>:-("

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
my_keywords = [' payed', ' definately', ' neccessary', ' occured', ' seperate']

# Received comments and messages arrays
unread_comments = []
unread_messages = []
unread_modmessages = []

# Main function
def run_grammarbot(reddit):
    print("Searching keywords in comment stream...")

    # Scrapes comments from all subreddits    
    for comment in reddit.subreddit(SUB).stream.comments():
        if comment.id not in posts_replied and comment.author.name != reddit.user.me:
            for keyword in my_keywords:
                if keyword in comment.body:
                    if keyword == ' payed':
                        correctSpelling = PAYED
                    elif keyword == ' definately':
                        correctSpelling = DEFINATELY
                    elif keyword == ' neccessary':
                        correctSpelling = NECCESSARY
                    elif keyword == ' occured':
                        correctSpelling = OCCURED
                    elif keyword == ' seperate':
                        correctSpelling = SEPERATE
        
                        try:
                            comment.reply(correctSpelling)
                            print("Replied to", comment.id, "written by", comment.author.name, "in", SUB)
                        except APIException:
                            with open("auto_grmrbt_bot.log","a") as f:
                                f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) + ": Rate Limit exception.\n")
                                time.sleep(600) # Equals ten minutes, roughly equal to Rate Limit
                                run_grammarbot(reddit)
                        except Exception as e:
                            print("General exception caught: ", e)
                            run_grammarbot(reddit)
                        finally:
                            run_grammarbot(reddit)

        # This loop searches inbox      
        for reply in reddit.inbox.unread(limit=None):
            try:
                print("Reply received...")

                # Handles three types of replies: messages, modmail and comments -- only responds to comments
                if isinstance(reply, Message):
                    print(reply.author.name, "has replied with a private message")
                    unread_messages.append(reply)
                    reddit.inbox.mark_read(unread_messages)
                    run_grammarbot(reddit)

                elif isinstance(reply, ModmailMessage):
                    print(reply.author.name, "has replied with a moderator message")
                    unread_modmessages.append(reply)
                    reddit.inbox.mark_read(unread_modmessages)
                    run_grammarbot(reddit)

                elif isinstance(reply, Comment):
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
                        elif reply.body.lower() == 'good bot':
                            reply.reply(GOOD_BOT)
                            print("Bot has replied with", GOOD_BOT)
                            run_grammarbot(reddit)        
                        elif reply.body.lower() == 'bad bot':
                            reply.reply(BAD_BOT)
                            print("Bot has replied with", BAD_BOT)
                            run_grammarbot(reddit)
                        else:
                            run_grammarbot(reddit)
                    else:
                        break

            except APIException:
                with open("auto_grmr_bot.log","a") as f:
                    f.write('{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()) + ": Rate Limit exception.\n")
                    run_grammarbot(reddit)
            except AttributeError:
                print("Caught an attribute error. Restarting...")
                run_grammarbot(reddit)
            finally:
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