# Nelson Dane
# Python bot to like, retweet, and reply to cashapp giveaways with a user's cashtag

# To Do:
# Allow custom searches
# Better logs
# Add a README
# Better date checker

# Importing the necessary modules
import os
import sys
import traceback
import datetime
import tweepy
import random
import datetime
from time import sleep
from dotenv import load_dotenv
import pytextnow as pytn

# CashApp ID Global Variable
CASHAPPID = '1445650784'

USERNAME = os.environ['username']
PHONE = os.environ['number']

client = pytn.Client(USERNAME) 

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

# Make sure the number of bearer/consumer/acess tokens (twitter accounts) and cashtags match
if len(BEARER_TOKENS) != len(CASHTAGS) != len(CONSUMER_KEYS) != len(CONSUMER_SECRETS) != len(ACCESS_TOKENS) != len(ACCESS_TOKEN_SECRETS) != len(USERNAMES):
    raise Exception("The number of usernames and cashtags must match the number of Twitter accounts")

# Get start and end time
if not os.environ["START_TIME"] or not os.environ["END_TIME"]:
    raise Exception("Please specify the start and end time in the .env file")
else:
    # Set the start and end time
    START_TIME = os.environ["START_TIME"]
    END_TIME = os.environ["END_TIME"]
    # Convert to float
    START_TIME = float(START_TIME)
    END_TIME = float(END_TIME)

# Get worded replies boolean, defaulting to False
WORDED_REPLIES = os.environ.get("WORDED_REPLIES", False)

# Get check interval, defaulting to 60 seconds
CHECK_INTERVAL_SECONDS = os.environ.get("CHECK_INTERVAL_SECONDS", 60)
# Convert to float
CHECK_INTERVAL_SECONDS = float(CHECK_INTERVAL_SECONDS)

# Replies to use (add more in future)
replies = [
    "I'd love some!",
    "This sounds awesome!",
    "Would really help out!"
]

# Function to follow Twitter accounts
def followAccount(client, accountID):
    try:
        client.follow_user(target_user_id=accountID,user_auth=True)
    except Exception as e:
        print(f'Error following {accountID}: {e}')

# Function to convert handle into ID
def idFromUsername(client, username):
    try:
        id = client.get_user(username=username,tweet_fields=['id'])
        return id.data.id
    except Exception as e:
        print(f'Error getting ID from {username}: {e}')

# Main program
def main_program():
    # Create client for each Twitter account and make sure they follow @CashApp
    Clients = []
    # Loop through each Twitter account
    for username in USERNAMES:
        # Set index for easy use
        i = USERNAMES.index(username)
        # Create client list
        Clients.append(tweepy.Client(bearer_token=BEARER_TOKENS[i],consumer_key=CONSUMER_KEYS[i], consumer_secret=CONSUMER_SECRETS[i], access_token=ACCESS_TOKENS[i], access_token_secret=ACCESS_TOKEN_SECRETS[i]))

    # Generate userID's and check if they follow @CashApp
    for username in USERNAMES:
        # Set index for easy use
        i = USERNAMES.index(username)
        # Get the user ID from the username
        userID = idFromUsername(Clients[i], username)
        # Check to see if account is following @cashapp
        # Get following list
        following = Clients[i].get_users_following(id=userID)
        # Check to see if @cashapp is in the following list, following if it isn't
        found = False
        for follow in following.data:
            if follow.username == "CashApp":
                print(f'{username} is already following @cashapp')
                found = True
                break
        if not found:
            followAccount(Clients[i], CASHAPPID)
            print(f'{username} just followed @CashApp')  
  
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

        # Search for cashapp giveaways.
        # Need to add ability to set custom search terms
        query = 'from:GamerSnail_ -is:retweet drop'

        # Search for tweets, using each account's client incase one hits the requests limit
        # I know I could set wait_on_rate, but since there's multiple accounts I'll just try them all
        for username in USERNAMES:
            try:
                # Set index for easy use
                i = USERNAMES.index(username)
                # Search for tweets that match the query
                tweets = Clients[i].search_recent_tweets(query=query, max_results=10)
                # Print total found giveaway tweets
                print(f'Found {len(tweets.data)} giveaway tweets!')

                client.send_sms(PHONE , "Giveaway found!")
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
            # Choose replies for each cashtag so that none of them use the same reply
            current_replies = random.sample(replies, len(CASHTAGS))
            # Loop through each cashtag
            for cashtag in CASHTAGS:
                i = CASHTAGS.index(cashtag)
                # Retweet the giveaway tweet
                Clients[i].retweet(giveaway_tweet.id,user_auth=True)
                print(f'Retweeted using: {USERNAMES[i]}')
                # Like the giveaway tweet
                Clients[i].like(giveaway_tweet.id,user_auth=True)
                print(f'Liked using: {USERNAMES[i]}')
                # Check if tweet is already replied to, and if not then reply to the giveaway tweet
                if not giveaway_tweet.id in recent_tweet_ids[i]:
                    if WORDED_REPLIES:
                        # Reply to the giveaway tweet with a worded reply
                        Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=f"current_replies[i] {CASHTAGS[i]}", user_auth=True)
                        print(f'{USERNAMES[i]} reply: {current_replies[i]}')
                    else:
                        # Reply to the giveaway tweet without a worded reply
                        Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=CASHTAGS[i], user_auth=True)
                        print(f'{USERNAMES[i]} reply: {CASHTAGS[i]}')
                else:
                    print(f'{USERNAMES[i]} already replied to this tweet, moving on...')
                # Sleep for a bit before next tweet
                sleep(random.uniform(1,5))
        # Sleep for a bit before rechecking for new giveaways
        print(f'All finished, sleeping for {CHECK_INTERVAL_SECONDS} seconds...')
        sleep(CHECK_INTERVAL_SECONDS)

# Run the main program if it's the correct time
try:
    # Only run if time is between wanted times
    if datetime.datetime.now().hour >= START_TIME and datetime.datetime.now().hour <= END_TIME:
        # Run the main program
        main_program()
    else:
        print(f'{datetime.datetime.now()} Not running because it is not between {START_TIME} and {END_TIME}')
        sleep(CHECK_INTERVAL_SECONDS)

# Get all exceptions
except Exception:
    print('Exited')
    print(f"Exception {traceback.format_exc()}")
    sys.exit(1)
