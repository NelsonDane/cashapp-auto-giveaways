# Nelson Dane and Prem (Sazn)
# Python bot to like, retweet, and reply to cashapp giveaways with a user's cashtag

import os
import sys
from tabnanny import check
import traceback
import datetime
import tweepy
import random
import datetime
from replies import replies
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

    # Check Twitter authentication are all the same length, rasie exception if not the case
    if (not (len(BEARER_TOKENS) == len(CONSUMER_KEYS) == len(CONSUMER_SECRETS) == len(ACCESS_TOKENS) == len(ACCESS_TOKEN_SECRETS))):
        raise Exception(f"Twitter authentication variables are not the same length.\nBEARER_TOKENS: {len(BEARER_TOKENS)}\nCONSUMER_KEYS: {len(CONSUMER_KEYS)}\nCONSUMER_SECRETS: {len(CONSUMER_SECRETS)}\nACCESS_TOKENS: {len(ACCESS_TOKENS)}\nACCESS_TOKEN_SECRETS: {len(ACCESS_TOKEN_SECRETS)}")
    else:
      print(f'Number of CashApp/Twitter Accounts: {len(CONSUMER_KEYS)}\n')

# Set the cashtags
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

# Get whether to check if following Cashapp or not
CHECK_FOLLOWING_CASHAPP = os.environ.get("CHECK_FOLLOWING_CASHAPP", False)
# Because it imports as string, convert to bool
if type(CHECK_FOLLOWING_CASHAPP) == str and (CHECK_FOLLOWING_CASHAPP.lower().replace(" ", "") == "true"):
    CHECK_FOLLOWING_CASHAPP = True
else:
    CHECK_FOLLOWING_CASHAPP = False

# Get start and end time, defaulting to 9:00am and 9:00pm
START_TIME = float(os.environ.get("START_TIME", "9"))
END_TIME = float(os.environ.get("END_TIME", "21"))

# Get worded replies boolean, defaulting to False
WORDED_REPLIES = os.environ.get("WORDED_REPLIES", False)
# Because it imports as string, convert to bool
if type(WORDED_REPLIES) == str and (WORDED_REPLIES.lower()).replace(" ", "") == 'true':
    WORDED_REPLIES = True
else:
    WORDED_REPLIES = False

# Make sure there's enough replies for each account
if (len(USERNAMES) > len(replies) and WORDED_REPLIES):
    print(f'Not enough replies for all Twitter accounts, disabling replies \t\t\t{datetime.datetime.now()}')
    WORDED_REPLIES = False

# Get check interval, defaulting to 15 minutes
CHECK_INTERVAL_SECONDS = float(os.environ.get("CHECK_INTERVAL_SECONDS", "900"))

# See if manual tweet is specified
if os.environ.get("MANUAL_TWEET"):
    # Set manual tweet id
    MANUAL_TWEET = os.environ.get("MANUAL_TWEET")
else:
    # Set manual tweet id to None
    MANUAL_TWEET = None

# Validation
# Make sure the number of bearer/consumer/acess tokens (twitter accounts), usernames, and cashtags match
if len(BEARER_TOKENS) != len(CASHTAGS) != len(CONSUMER_KEYS) != len(CONSUMER_SECRETS) != len(ACCESS_TOKENS) != len(ACCESS_TOKEN_SECRETS) != len(USERNAMES) != len(CASHTAGS):
    raise Exception("The number of usernames and cashtags must match the number of Twitter accounts")

# Remove whitespaces from API tokens and keys, and $/@ from cashtags and usernames
for i in range(len(USERNAMES)):
    BEARER_TOKENS[i] = BEARER_TOKENS[i].replace(" ", "")
    CONSUMER_KEYS[i] = CONSUMER_KEYS[i].replace(" ", "")
    CONSUMER_SECRETS[i] = CONSUMER_SECRETS[i].replace(" ", "")
    ACCESS_TOKENS[i] = ACCESS_TOKENS[i].replace(" ", "")
    ACCESS_TOKEN_SECRETS[i] = ACCESS_TOKEN_SECRETS[i].replace(" ", "")
    CASHTAGS[i] = (CASHTAGS[i].replace(" ", "")).replace("$", "")
    USERNAMES[i] = (USERNAMES[i].replace(" ", "")).replace("@", "")

# Make sure start and end times are valid
if START_TIME > END_TIME:
    raise Exception("Start time must be before end time")

# Functions

# Function to check if cached tweets file exists, creating it if it doesn't
def cached_tweets_init():
    if not os.path.isfile("cached_tweets.txt"):
        open("cached_tweets.txt", "a").close()
        print(f"Created new cached_tweets.txt file \t\t\t{datetime.datetime.now()}")
        print()
    else:
        print(f"cached_tweets.txt file already exists \t\t\t{datetime.datetime.now()}")
        print()

# Function to check if tweet id exists in cached tweets file
def check_cached_tweets(tweet_id):
    # Open cached tweets file
    with open("cached_tweets.txt") as f:
        # Read each line
        lines = f.readlines()
        # Strip newline characters
        lines = [line.strip() for line in lines]
        # Check if tweet id is in the file
        if str(tweet_id) in lines:
            print(f"Tweet {tweet_id} found in cache \t\t\t{datetime.datetime.now()}")
            return True
        else:
            return False

def append_cached_tweets(tweet_id):
    # Open cached tweets file
    with open("cached_tweets.txt", "a") as f:
        # Write tweet id to file
        f.write(f"{tweet_id}\n")
        print(f"Appended {tweet_id} to cached_tweets.txt \t\t{datetime.datetime.now()}")

def close_cached_tweets():
    print(f"Closing cached_tweets.txt \t\t\t{datetime.datetime.now()}")
    # Close cached tweets file
    with open("cached_tweets.txt", "a") as f:
        f.close()

# Function to follow Twitter accounts
def followAccount(client, currentUsername, usernameToFollow):
    # Get the user ID from the username
    userID = idFromUsername(client, currentUsername)
    followID = idFromUsername(client, usernameToFollow)
    # Check to see if account is following already
    # Get following list
    if not userID and not followID:
        try:
            following = client.get_users_following(id=userID)
        except tweepy.errors.TooManyRequests as e:
            print(f"Rate limit exceeded on {currentUsername}: {e} \t\t{datetime.datetime.now()}")
            return
        # Check to see if it is in the following list, following if it isn't
        found = False
        if following is not None:
            for follow in following.data:
                if follow.username == usernameToFollow:
                    print(f'{currentUsername} is already following {usernameToFollow}\t\t\t{datetime.datetime.now()} ')
                    found = True
                    break
            if not found:
                try:
                    client.follow_user(target_user_id=followID, user_auth=True)
                    print(f'{currentUsername} just followed {usernameToFollow} \t\t\t {datetime.datetime.now()} ')
                except Exception as e:
                    print(f'Error following {usernameToFollow} with {currentUsername}: {e} \t\t\t{datetime.datetime.now()} ')
        else:
            # If following is None, then just follow the user
            try:
                client.follow_user(target_user_id=followID, user_auth=True)
                print(f'{currentUsername} just followed {usernameToFollow} \t\t\t{datetime.datetime.now()} ')
            except Exception as e:
                print(f'Error following {usernameToFollow} with {currentUsername}: {e} \t\t\t{datetime.datetime.now()} ')

# Function to convert handle into ID
def idFromUsername(client, username):
    try:
        id = client.get_user(username=username, tweet_fields=['id'])
        return id.data.id
    except Exception as e:
        print(f'Error getting ID from {username}: {e} \t\t\t {datetime.datetime.now()} ')

# Function to get username from ID
def usernameFromID(client, id):
    try:
        username = client.get_user(id=id, user_fields=['username'])
        return username.data.username
    except Exception as e:
        print(f'Error getting username from {id}: {e} \t\t\t{datetime.datetime.now()} ')

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
    return (hashtags.replace("#", " #")).strip()

# Function to find mentions
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
        if letter.isspace():
            atFound = False
        # If none above is true, then add the letter to the username
        elif atFound:
            usernames += letter
    # Hacky, but add space in front of @, then remove trailing whitespace and return
    final = (usernames.replace("@", " @")).strip()
    # Remove unwanted characters
    unwanted = [',','.',':',';','!','?','(',')','[',']','{','}','<','>','+','=','*','&','%','$','#','^','~','`','|','\\','\'','"']
    for char in unwanted:
        final = final.replace(char, '')
    return final

# Main program
def main_program():
    run_main = False
    while not run_main:
        # Kill the program if the time is outside of the start and end times
        if (datetime.datetime.now().hour >= START_TIME and datetime.datetime.now().hour <= END_TIME):
            run_main = True
        else:
            print(f'Not running because it is not between {START_TIME} and {END_TIME} \t\t {datetime.datetime.now()}')
            sleep(CHECK_INTERVAL_SECONDS)

    # Create client for each Twitter account and make sure they follow @CashApp
    Clients = []
    # Loop through each Twitter account
    for username in USERNAMES:
        # Set index for easy use
        i = USERNAMES.index(username)
        # Create client list
        Clients.append(tweepy.Client(bearer_token=BEARER_TOKENS[i], consumer_key=CONSUMER_KEYS[i],
                       consumer_secret=CONSUMER_SECRETS[i], access_token=ACCESS_TOKENS[i], access_token_secret=ACCESS_TOKEN_SECRETS[i]))

    # Generate userID's and check if they follow @CashApp if enabled
    if CHECK_FOLLOWING_CASHAPP:
        for client in Clients:
            # Set index for easy use
            i = Clients.index(client)
            try:
                followAccount(client, USERNAMES[i], "CashApp")
            except tweepy.errors.TooManyRequests as e:
                print(f'Error following CashApp with {USERNAMES[i]}: {e} \t\t\t{datetime.datetime.now()} ')

    # Initialize cached tweets file
    cached_tweets_init()

    # Run search forever
    while True:
        # Update recent tweets from each user
        recent_tweet_ids = []
        # Set final list of tweets list
        final_list = []
        for client in Clients:
            # Set index for easy use
            i = Clients.index(client)
            # Create sublist
            sub_recent_tweets = []
            # Get recent tweets
            recent_tweets = client.get_users_tweets(id=idFromUsername(
                client, USERNAMES[i]), user_auth=True, tweet_fields=['conversation_id'])
            # Create list in list: list-ception
            # Make sure recent_tweets isn't None
            if recent_tweets is not None:
                for tweet in (recent_tweets.data):
                    sub_recent_tweets.append(tweet.conversation_id)
                recent_tweet_ids.append(sub_recent_tweets)

        # Search for liked tweets by CashApp if manual search is not enabled
        if not MANUAL_TWEET:
            for username in USERNAMES:
                # Search for liked tweets by CashApp
                try:
                    # Set index for easy use
                    i = USERNAMES.index(username)
                    # Get liked tweets by CashApp
                    print(f'\nSearching for liked tweets by CashApp...\t\t {datetime.datetime.now()} \n')
                    liked_tweets = Clients[i].get_liked_tweets(
                        id=CASHAPPID, user_auth=True, tweet_fields=['author_id'])
                    # If the search was successful, break out of the loop
                    break
                except Exception as e:
                    print(f'Failed getting liked tweets by CashApp: {e} {datetime.datetime.now()} ')
                    if i == len(USERNAMES)-1:
                        print(f'Failed to search for tweets using any account, exiting... {datetime.datetime.now()} ')
                        sys.exit(1)
                    else:
                        print(f'Trying with another account... {datetime.datetime.now()} ')
            for username in USERNAMES:
                # Search for tweets from CashApp
                try:
                    # Set index for easy use
                    i = USERNAMES.index(username)
                    # Get tweets from CashApp
                    print(f'\nSearching for tweets from CashApp...\t\t {datetime.datetime.now()} \n')
                    cashapp_tweets = Clients[i].get_users_tweets(id=CASHAPPID, user_auth=True, tweet_fields=['author_id'])
                    # If the search was successful, break out of the loop
                    break
                except Exception as e:
                    print(f'Failed getting tweets from CashApp: {e} {datetime.datetime.now()} ')
                    if i == len(USERNAMES)-1:
                        print(f'Failed to search for tweets using any account, exiting... {datetime.datetime.now()} ')
                        sys.exit(1)
                    else:
                        print(f'Trying with another account... {datetime.datetime.now()} ')
        else:
            # Use manual search
            print(f'Manual Tweet ID set to: {MANUAL_TWEET} \t\t\t {datetime.datetime.now()} ')
            final_list = Clients[1].get_tweet(id=MANUAL_TWEET, tweet_fields=['author_id'], user_auth=True)
            run_once = True
        # Search for tweets that contain "drop" or "must follow" unless manual search is enabled
        if not MANUAL_TWEET:
            run_once = False
            keywords = ['drop','must follow','partnered','your $cashtag','below','partner', 'giveaway', 'give away','chance to win','must follow to win', 'celebrate']
            # Search liked tweets by CashApp
            for tweet in liked_tweets.data:
                if any(x in tweet.text.lower() for x in keywords) and (not check_cached_tweets(tweet.id)):
                    final_list.append(tweet)
            # Search tweets from CashApp
            for tweet in cashapp_tweets.data:
                if any(x in tweet.text.lower() for x in keywords) and (not check_cached_tweets(tweet.id)):
                    final_list.append(tweet)
            if final_list == []:
                print(f'No tweets found that match the keywords \t\t\t{datetime.datetime.now()}')

        # Loop through the tweets and process them
        for giveaway_tweet in final_list:
            print(giveaway_tweet.text)
            # Get user mentions
            try:
                mentions = findMentions(giveaway_tweet.text)
            except Exception as e:
                print(f'Failed getting mentions, skipping: {e} {datetime.datetime.now()} ')
                mentions = ""
            mentionsList = mentions.replace("@", "").split(" ")
            # Get hashtags
            hashtags = findHashtags(giveaway_tweet.text)
            # Choose replies for each cashtag so that none of them use the same reply
            current_replies = random.sample(replies, len(CASHTAGS))
            print()
            # Loop through each cashtag
            for username in USERNAMES:
                i = USERNAMES.index(username)
                # Check if tweet is already replied to, and if not then continue to the giveaway tweet
                if not giveaway_tweet.id in recent_tweet_ids[i]:
                    # Follow all mentioned users in giveaway tweet
                    if mentions:
                        for mention in mentionsList:
                            # Set index for easy use
                            j = mentionsList.index(mention)
                            # Follow mentioned user
                            followAccount(Clients[j], USERNAMES[j], mention)
                    # Follow author of giveaway tweet
                    author_usename = usernameFromID(
                        Clients[i], giveaway_tweet.author_id)
                    print()
                    followAccount(Clients[i], username, author_usename)
                    # Retweet the giveaway tweet
                    Clients[i].retweet(giveaway_tweet.id, user_auth=True)
                    print(f'Retweeted using: {username}')
                    # Like the giveaway tweet
                    Clients[i].like(giveaway_tweet.id, user_auth=True)
                    print(f'Liked using: {username}')
                    # Replies section
                    try:
                        # Check if worded replies is enabled
                        if WORDED_REPLIES:
                            message = f"{current_replies[i]} {mentions} @{author_usename} {hashtags} ${CASHTAGS[i]}"
                            # Reply to the giveaway tweet with a worded reply
                            Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id, text=message, user_auth=True)
                            # Quote retweet the giveaway tweet with a worded reply
                            Clients[i].create_tweet(quote_tweet_id=giveaway_tweet.id, text=message, user_auth=True)
                            print(f'{username} reply: {message}')
                            print()
                        else:
                            message = f"${CASHTAGS[i]} {hashtags} {mentions} @{author_usename}"
                            # Reply to the giveaway tweet without a worded reply
                            Clients[i].create_tweet(in_reply_to_tweet_id=giveaway_tweet.id,text=message, user_auth=True)
                            # Quote retweet the giveaway tweet without a worded reply
                            Clients[i].create_tweet(quote_tweet_id=giveaway_tweet.id, text=message, user_auth=True)
                            print(f'{username} reply: {message}')
                            print()
                    except tweepy.errors.Forbidden:
                        print(f'Error replying to tweet with {username}: Forbidden \t\t\t{datetime.datetime.now()}')
                    except Exception as e:
                        print(f'Error replying to tweet with {username}: {e} \t\t\t{datetime.datetime.now()}')
                else:
                    print(f'{username} already replied to this tweet, moving on... \t\t\t{datetime.datetime.now()}')
            # If manual search is enabled, break out of the loop
            if run_once:
                break
            # Append the tweet ID to the cached tweet file
            append_cached_tweets(giveaway_tweet.id)
            # Sleep for a bit before next tweet
            sleep(random.uniform(1, 5))

        # If manual search is completed, then exit gracefully
        if MANUAL_TWEET:
            print(f'\nAll finished, exiting... {datetime.datetime.now()} ')
            sys.exit(0)
        else:
            # Sleep for a bit before rechecking for new giveaways
            print(f'\nAll finished, sleeping for {CHECK_INTERVAL_SECONDS/60} minutes...\t\t\t {datetime.datetime.now()}')
            sleep(CHECK_INTERVAL_SECONDS)

# Run the main program if it's the correct time
try:
    main_program()

# Get all exceptions
except KeyboardInterrupt:
    print(f'\nDetected KeyboardInterrupt. Exiting... {datetime.datetime.now()} ')
    sys.exit(0)
except Exception:
    print('Exited')
    print(f"Exception {traceback.format_exc()}")
    sys.exit(1)
