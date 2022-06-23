# Nelson Dane
# Python bot to reply, retweet, and like to cashapp giveaways with a user's cashtag

# Importing the necessary modules
import os
import sys
import traceback
import datetime
import tweepy
import random
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

# Make sure the number of bearer/consumer/acess tokens (twitter accounts) and cashtags match
if len(BEARER_TOKENS) != len(CASHTAGS) != len(CONSUMER_KEYS) != len(CONSUMER_SECRETS) != len(ACCESS_TOKENS) != len(ACCESS_TOKEN_SECRETS):
    raise Exception("The number of cashtags must match the number of Twitter accounts")

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
        #print(f'Followed account ID: {accountID}')
    except Exception as e:
        print(f'Error following {accountID}: {e}')
    
# Main program
def main_program():
    # Run forever
    while True:
        # Create client for each Twitter account and make sure they follow @CashApp
        Clients = []
        # Loop through each Twitter account
        for CASHTAG in CASHTAGS:
            # Set index for easy use
            i = CASHTAGS.index(CASHTAG)
            # Create client list
            Clients.append(tweepy.Client(bearer_token=BEARER_TOKENS[i],consumer_key=CONSUMER_KEYS[i], consumer_secret=CONSUMER_SECRETS[i], access_token=ACCESS_TOKENS[i], access_token_secret=ACCESS_TOKEN_SECRETS[i]))
   
            # Figure out how to get user ID later
            id2 = Clients[i].get_user(username='GamerSnail_')
            id = id2.data.id
            # Check to see if account is following @cashapp
            # Get following list
            following = Clients[i].get_users_following(id=id)
            # Check to see if @cashapp is in the following list
            for follow in following.data:
                if follow.username == "CashApp":
                    print(f'{CASHTAG} is already following @cashapp')
                    break
                else:
                    followAccount(Clients[i], CASHAPPID)
                    print(f'{CASHTAG} just followed @CashApp')         

        # Search for cashapp giveaways. We only cover the ones directly from cashapp
        # and they almost always use the term 'drop' when referring to cashtags and giveaways
        query = 'from:GamerSnail_ drop'

        # Search for tweets, using each account's client incase one hits the requests limit
        for CASHTAG in CASHTAGS:
            try:
                # Set index for easy use
                i = CASHTAGS.index(CASHTAG)
                # Search for tweets that match the query
                tweets = Clients[i].search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'], max_results=10)
                # Print total found giveaway tweets
                print(f'Found {len(tweets.data)} giveaway tweets!')
                # If the search was successful, then break out of loop
                break
            except Exception as e:
                print(f'{datetime.datetime.now()} Failed to search for tweets using account {CASHTAGS[i]}: {e}')
                if i==len(CASHTAGS)-1:
                    print(f'{datetime.datetime.now()} Failed to search for tweets using any account, exiting')
                    sys.exit(1)
                else:
                    print('Trying with another account...')

        # Loop through the tweets and process them. Add try-excepts later
        for giveaway_tweet in tweets.data:
            #print('Giveaway tweet found!')
            print(giveaway_tweet.text)
            # Choose replies for each cashtag so that none of them use the same reply
            current_replies = random.sample(replies, len(CASHTAGS))
            # Loop through each cashtag
            for cashtag in CASHTAGS:
                i = CASHTAGS.index(cashtag)
                # Retweet the giveaway tweet
                Clients[i].retweet(giveaway_tweet.id,user_auth=True)
                print(f'Retweeted using cashtag: {cashtag}')
                # Like the giveaway tweet
                Clients[i].like(giveaway_tweet.id,user_auth=True)
                print(f'Liked using cashtag: {cashtag}')
                # Reply to the giveaway tweet
                Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=current_replies[CASHTAGS.index(cashtag)], user_auth=True)
                print(f'Replied using cashtag: {cashtag}')
                print(f'Reply: {current_replies[CASHTAGS.index(cashtag)]}')
                # Sleep for a bit
                sleep(5)
        # Sleep for a bit
        print('Sleeping for a bit...')
        sleep(60)

# Run the main program
try:
    main_program()

# Get all exceptions
except Exception:
    print('Exited')
    print(f"Exception {traceback.format_exc()}")
    sys.exit(1)
