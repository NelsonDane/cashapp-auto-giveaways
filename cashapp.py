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

# Main program
def main_program():
    # Run forever
    while True:
        # Setup the Twitter API with bearer token of random account
        api = random.randint(0, len(BEARER_TOKENS)-1)
        client = tweepy.Client(bearer_token=BEARER_TOKENS[api],consumer_key=CONSUMER_KEYS[api], consumer_secret=CONSUMER_SECRETS[api], access_token=ACCESS_TOKENS[api], access_token_secret=ACCESS_TOKEN_SECRETS[api])

        # Search for cashapp giveaways. We only cover the ones directly from cashapp
        # and they almost always use the term 'drop' when referring to cashtags and giveaways
        query = 'from:GamerSnail_ drop'

        # Search for tweets
        try:
            tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'], max_results=10)
        except Exception as e:
            print(f'{datetime.datetime.now()} Failed to search for tweets using account {api}: {e}')
            print('Trying with another account...')

        # Loop through the tweets and process them. Add try-excepts later
        for giveaway_tweet in tweets.data:
            print('Giveaway tweet found!')
            print(giveaway_tweet.text)
            # Choose replies for each cashtag so that none of them use the same reply
            current_replies = random.sample(replies, len(CASHTAGS))
            # Loop through each cashtag
            for cashtag in CASHTAGS:
                # Retweet the giveaway tweet
                client.retweet(giveaway_tweet.id,user_auth=True)
                print(f'Retweeted using cashtag: {cashtag}')
                # Like the giveaway tweet
                client.like(giveaway_tweet.id,user_auth=True)
                print(f'Liked using cashtag: {cashtag}')
                # Reply to the giveaway tweet
                client.create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=current_replies[CASHTAGS.index(cashtag)], user_auth=True)
                print(f'Replied using cashtag: {cashtag}')
                print(f'Reply: {current_replies[CASHTAGS.index(cashtag)]}')
        # Sleep for a bit
        sleep(60)

# Run the main program
try:
    main_program()

# Get all exceptions
except Exception:
    print('Exited')
    print(f"Exception {traceback.format_exc()}")
    sys.exit(1)
