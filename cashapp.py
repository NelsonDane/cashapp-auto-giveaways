# Nelson Dane
# Python bot to like, retweet, and reply to cashapp giveaways with a user's cashtag

# Importing the necessary modules
import os
import sys
import traceback
import datetime
import tweepy
import random
import datetime
from replies import replies
from searches import searches
from time import sleep
from dotenv import load_dotenv

# CashApp ID Global Variable
CASHAPPID = '1445650784'

# Load the .env file
load_dotenv()

# Raise error if needed variables are not specified
if not os.environ["BEARER_TOKENS"] or not os.environ["CONSUMER_KEYS"] or not os.environ["CONSUMER_SECRETS"] or not os.environ["ACCESS_TOKENS"] or not os.environ["ACCESS_TOKEN_SECRETS"]:
    raise Exception("Please specify the needed variables for Twitter authentication in the .env file")
else:
    # Set the twitter authentication variables
    BEARER_TOKENS = os.environ["BEARER_TOKENS"].split(",")
    CONSUMER_KEYS = os.environ["CONSUMER_KEYS"].split(",")
    CONSUMER_SECRETS = os.environ["CONSUMER_SECRETS"].split(",")
    ACCESS_TOKENS = os.environ["ACCESS_TOKENS"].split(",")
    ACCESS_TOKEN_SECRETS = os.environ["ACCESS_TOKEN_SECRETS"].split(",")

if not os.environ["CASHTAGS"]:
    raise Exception("Please specify the cashtags in the .env file")
else:
    # Set the cashtags
    CASHTAGS = os.environ["CASHTAGS"].split(",")

# Set the usernames
if not os.environ["USERNAMES"]:
    raise Exception("Please specify the usernames in the .env file")
else:
    # Set the hashtags
    USERNAMES = os.environ["USERNAMES"].split(",")

# Get start and end time, defaulting to 9:00am and 9:00pm
START_TIME = float(os.environ.get("START_TIME","9"))
END_TIME = float(os.environ.get("END_TIME","21"))

# Get worded replies boolean, defaulting to False
WORDED_REPLIES = os.environ.get("WORDED_REPLIES", False)
# Because it imports as string, convert to bool
if type(WORDED_REPLIES) == str and (WORDED_REPLIES.lower()).replace(" ","") == 'true':
    WORDED_REPLIES = True
else:
    WORDED_REPLIES = False

# Make sure there's enough replies for each account
if len(USERNAMES) > len(replies):
    print("Not enough replies for all Twitter accounts, disabling replies")
    WORDED_REPLIES = False

# Get check interval, defaulting to 60 seconds
CHECK_INTERVAL_SECONDS = float(os.environ.get("CHECK_INTERVAL_SECONDS", "60"))

# Validation
# Make sure the number of bearer/consumer/acess tokens (twitter accounts) and cashtags match
if len(BEARER_TOKENS) != len(CASHTAGS) != len(CONSUMER_KEYS) != len(CONSUMER_SECRETS) != len(ACCESS_TOKENS) != len(ACCESS_TOKEN_SECRETS) != len(USERNAMES):
    raise Exception("The number of usernames and cashtags must match the number of Twitter accounts")

# Remove whitespaces from API tokens and keys, and $/@ from cashtags and usernames
for i in range(len(USERNAMES)):
    BEARER_TOKENS[i] = BEARER_TOKENS[i].replace(" ","")
    CONSUMER_KEYS[i] = CONSUMER_KEYS[i].replace(" ","")
    CONSUMER_SECRETS[i] = CONSUMER_SECRETS[i].replace(" ","")
    ACCESS_TOKENS[i] = ACCESS_TOKENS[i].replace(" ","")
    ACCESS_TOKEN_SECRETS[i] = ACCESS_TOKEN_SECRETS[i].replace(" ","")
    CASHTAGS[i] = (CASHTAGS[i].replace(" ","")).replace("$","")
    USERNAMES[i] = (USERNAMES[i].replace(" ","")).replace("@","")

# Make sure start and end times are valid
if START_TIME > END_TIME:
    raise Exception("Start time must be before end time")

# Function to follow Twitter accounts
def followAccount(client, currentUsername, usernameToFollow):
    # Get the user ID from the username
    userID = idFromUsername(client, currentUsername)
    followID = idFromUsername(client, usernameToFollow)
    # Check to see if account is following already
    # Get following list
    following = client.get_users_following(id=userID)
    # Check to see if it is in the following list, following if it isn't
    found = False
    for follow in following.data:
        if follow.username == usernameToFollow:
            print(f'{currentUsername} is already following {usernameToFollow}')
            found = True
            break
    if not found:
        try:
            client.follow_user(target_user_id=followID, user_auth=True)
            print(f'{currentUsername} just followed {usernameToFollow}')  
        except Exception as e:
            print(f'Error following {usernameToFollow} with {currentUsername}: {e}')

# Function to convert handle into ID
def idFromUsername(client, username):
    try:
        id = client.get_user(username=username,tweet_fields=['id'])
        return id.data.id
    except Exception as e:
        print(f'Error getting ID from {username}: {e}')

def usernameFromID(client, id):
    try:
        username = client.get_user(id=id,user_fields=['username'])
        return username.data.username
    except Exception as e:
        print(f'Error getting username from {id}: {e}')

# Function to find mentions and hastags
def findHashtags(tweet):
    # Start found at false
    hashFound = False
    # Create hashtags string
    hashtags = ""
    # Iterate through each character
    for letter in tweet:
        # If hashtag found, then it's a hashtag
        if letter == "#":
            hashFound = True
        # If a space if found, then it's the end of the hashtag
        if letter == " ":
            hashFound = False
        # If none above is true, then add the letter to the hashtag
        elif hashFound:
            hashtags += letter
    # Hacky, but add space in front of #, then remove trailing whitespace and return
    return (hashtags.replace("#"," #")).strip()

def findMentions(tweet):
    # Start found at false
    atFound = False
    # Create mentions string
    usernames = ""
    # Iterate through each character
    for letter in tweet:
        # If at sign found, then it's a user mention
        if letter == "@":
            atFound = True
        # If a space if found, then it's the end of the mention
        if letter == " ":
            atFound = False
        # If none above is true, then add the letter to the username
        elif atFound:
            usernames += letter
    # Hacky, but add space in front of #, then remove trailing whitespace and return
    return (usernames.replace("@"," @")).strip()

# Main program
def main_program():
    run_main = False
    while not run_main:
        # Kill the program if the time is outside of the start and end times
        if (datetime.datetime.now().hour >= START_TIME and datetime.datetime.now().hour <= END_TIME):
            run_main = True
        else:
            print(f'{datetime.datetime.now()} Not running because it is not between {START_TIME} and {END_TIME}')
            sleep(CHECK_INTERVAL_SECONDS)

    # Create client for each Twitter account and make sure they follow @CashApp
    Clients = []
    # Loop through each Twitter account
    for username in USERNAMES:
        # Set index for easy use
        i = USERNAMES.index(username)
        # Create client list
        Clients.append(tweepy.Client(bearer_token=BEARER_TOKENS[i],consumer_key=CONSUMER_KEYS[i], consumer_secret=CONSUMER_SECRETS[i], access_token=ACCESS_TOKENS[i], access_token_secret=ACCESS_TOKEN_SECRETS[i]))

    # Generate userID's and check if they follow @CashApp
    for client in Clients:
        # Set index for easy use
        i = Clients.index(client)
        followAccount(client, USERNAMES[i], "CashApp")

    # Run search forever
    while True:
        # Update recent tweets from each user
        recent_tweet_ids = []
        for client in Clients:
            # Set index for easy use
            i = Clients.index(client)
            # Create sublist
            sub_recent_tweets = []
            # Get recent tweets
            recent_tweets = client.get_users_tweets(id=idFromUsername(client,USERNAMES[i]), user_auth=True, tweet_fields=['conversation_id'])
            # Create list in list: list-ception
            for tweet in (recent_tweets.data):
                sub_recent_tweets.append(tweet.conversation_id)
            recent_tweet_ids.append(sub_recent_tweets)

        # Search for tweets, using each account's client incase one hits the requests limit
        # I know I could set wait_on_rate, but since there's multiple accounts I'll just try them all
        for username in USERNAMES:
            try:
                # Set index for easy use
                i = USERNAMES.index(username)
                # Search for tweets that match the query
                tweets = Clients[i].search_recent_tweets(query=searches, max_results=10, tweet_fields=['author_id'])
                # Print total found giveaway tweets
                print(f'Found {len(tweets.data)} giveaway tweets!')
                # If the search was successful, then break out of loop
                break
            except Exception as e:
                print(f'{datetime.datetime.now()} Failed to search for tweets using account {USERNAMES[i]}: {e}')
                if i==len(USERNAMES)-1:
                    print(f'{datetime.datetime.now()} Failed to search for tweets using any account, exiting...')
                    sys.exit(1)
                else:
                    print('Trying with another account...')

        # Loop through the tweets and process them
        for giveaway_tweet in tweets.data:
            print(giveaway_tweet.text)
            # Get user mentions
            mentions = findMentions(giveaway_tweet.text)
            mentionsList = mentions.replace("@","").split(" ")
            # Get hashtags
            hashtags = findHashtags(giveaway_tweet.text)
            # Choose replies for each cashtag so that none of them use the same reply
            current_replies = random.sample(replies, len(CASHTAGS))
            # Loop through each cashtag
            for username in USERNAMES:
                i = USERNAMES.index(username)
                # Check if tweet is already replied to, and if not then continue to the giveaway tweet
                if not giveaway_tweet.id in recent_tweet_ids[i]:
                    # Follow all mentioned users in giveaway tweet
                    if mentions:
                        for mention in mentionsList:
                            # Set index for easy use
                            i = mentionsList.index(mention)
                            # Follow mentioned user
                            followAccount(Clients[i], username, mention)
                    # Follow author of giveaway tweet
                    followAccount(Clients[i], username, usernameFromID(Clients[i], giveaway_tweet.author_id))
                    # Retweet the giveaway tweet
                    Clients[i].retweet(giveaway_tweet.id,user_auth=True)
                    print(f'Retweeted using: {USERNAMES[i]}')
                    # Like the giveaway tweet
                    Clients[i].like(giveaway_tweet.id,user_auth=True)
                    print(f'Liked using: {USERNAMES[i]}')
                    if WORDED_REPLIES:
                        # Reply to the giveaway tweet with a worded reply
                        Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=f"{current_replies[i]} {mentions} {hashtags} ${CASHTAGS[i]}", user_auth=True)
                        print(f'{USERNAMES[i]} reply: {current_replies[i]} {mentions} {hashtags} ${CASHTAGS[i]}')
                    else:
                        # Reply to the giveaway tweet without a worded reply
                        Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=f"{mentions} {hashtags} ${CASHTAGS[i]}", user_auth=True)
                        print(f'{USERNAMES[i]} reply: {mentions} {hashtags} ${CASHTAGS[i]}')
                else:
                    print(f'{USERNAMES[i]} already replied to this tweet, moving on...')
            # Sleep for a bit before next tweet
            sleep(random.uniform(1,5))
        # Sleep for a bit before rechecking for new giveaways
        print(f'All finished, sleeping for {CHECK_INTERVAL_SECONDS} seconds...')
        sleep(CHECK_INTERVAL_SECONDS)

# Run the main program if it's the correct time
try:
    main_program()

# Get all exceptions
except Exception:
    print('Exited')
    print(f"Exception {traceback.format_exc()}")
    sys.exit(1)
