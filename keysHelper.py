import os
import dotenv
from dotenv import load_dotenv

load_dotenv()
try:
    cashtags = os.environ['cashtags'].split(",")
except:
    cashtags = 'your, multiple, cashtags, here'.split(",")

BEARER_TOKENS, CONSUMER_KEYS, CONSUMER_SECRETS, ACCESS_TOKENS, ACCESS_TOKEN_SECRETS= '','','','',''

for tags in cashtags:
    BEARER_TOKENS += (input(f'{tags}\'s BEARER TOKEN: ') + ',')
    CONSUMER_KEYS += (input(f'{tags}\'s CONSUMER KEY: ') + ',')
    CONSUMER_SECRETS += (input(f'{tags}\'s CONSUMER SECRET: ') + ',')
    ACCESS_TOKENS += (input(f'{tags}\'s ACCESS TOKEN: ') + ',')
    ACCESS_TOKEN_SECRETS += (input(f'{tags}\'s ACCESS TOKEN SECRET: ') + ',')
    print()

print(f'BEARER_TOKENS ={BEARER_TOKENS}\nCONSUMER_KEYS ={CONSUMER_KEYS}\nCONSUMER_SECRETS ={CONSUMER_SECRETS}\nACCESS_TOKENS ={ACCESS_TOKENS}\nACCESS_TOKEN_SECRETS ={ACCESS_TOKEN_SECRETS}')


