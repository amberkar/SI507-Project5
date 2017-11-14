import csv
from datetime import datetime
import json
import requests_oauthlib
import secret_data
import webbrowser


## CACHING SETUP ##

### Constants ###
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = "cache_contents.json"
CREDS_CACHE_FILE = "creds.json"
###/Constants ###

### Cache Files ###
#### data cache ####
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}
#### /data cache ####

#### creds cache ####
try:
    with open(CREDS_CACHE_FILE,'r') as creds_file:
        cache_creds = creds_file.read()
        CREDS_DICTION = json.loads(cache_creds)
except:
    CREDS_DICTION = {}
#### /creds cache ####


### Cache Functions ###
def has_cache_expired(timestamp_str, expire_in_days):
    now = datetime.now()
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
    delta = now - cache_timestamp
    delta_in_days = delta.days

    if delta_in_days > expire_in_days:
        return True
    else:
        return False

def get_from_cache(identifier, dictionary):
    identifier = identifier.upper()
    if identifier in dictionary:
        data_assoc_dict = dictionary[identifier]
        if has_cache_expired(data_assoc_dict['timestamp'],data_assoc_dict["expire_in_days"]):
            if DEBUG:
                print("Cache has expired for {}".format(identifier))
            del dictionary[identifier]
            data = None
        else:
            data = dictionary[identifier]['values']
    else:
        data = None
    return(data)


def set_in_data_cache(identifier, data, expire_in_days):
    identifier = identifier.upper()
    CACHE_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

def set_in_creds_cache(identifier, data, expire_in_days):
    identifier = identifier.upper()
    CREDS_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CREDS_CACHE_FILE, 'w') as cache_file:
        cache_json = json.dumps(CREDS_DICTION)
        cache_file.write(cache_json)
### /Cache Functions ###
## /CACHING SETUP ##

## OAUTH ##

### API Constants ###
CLIENT_KEY = secret_data.client_key
CLIENT_SECRET = secret_data.client_secret
REQUEST_TOKEN_URL = "https://www.tumblr.com/oauth/request_token"
BASE_AUTH_URL = "https://www.tumblr.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://www.tumblr.com/oauth/access_token"
### /API Constants ###

### OAuth Functions ###
def get_tokens(client_key=CLIENT_KEY, client_secret=CLIENT_SECRET,request_token_url=REQUEST_TOKEN_URL,base_authorization_url=BASE_AUTH_URL,access_token_url=ACCESS_TOKEN_URL,verifier_auto=False):
    oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret=client_secret)
    fetch_response = oauth_inst.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    auth_url = oauth_inst.authorization_url(base_authorization_url)

    webbrowser.open(auth_url)

    if verifier_auto:
        verifier = input("Please input the verifier:  ")
    else:
        redirect_result = input("Paste the full redirect URL here:  ")
        oauth_resp = oauth_inst.parse_authorization_response(redirect_result)
        verifier = oauth_resp.get('oauth_verifier')

    oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier)
    oauth_tokens = oauth_inst.fetch_access_token(access_token_url)
    resource_owner_key, resource_owner_secret = oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret')

    return client_key, client_secret, resource_owner_key, resource_owner_secret, verifier

def get_tokens_from_service(service_name_ident, expire_in_days=7):
    creds_data = get_from_cache(service_name_ident, CREDS_DICTION)
    if creds_data:
        if DEBUG:
            print("Loading creds from cache...")
            print()
    else:
        if DEBUG:
            print("Fetching fresh creds...")
            print("Prepare to log in via browser.")
            print()
        creds_data = get_tokens()
        set_in_creds_cache(service_name_ident, creds_data, expire_in_days=expire_in_days)

    return creds_data

def create_request_identifier(url, params_diction):
    sorted_params = sorted(params_diction.items(),key=lambda x:x[0])
    params_str = "_".join([str(e) for l in sorted_params for e in l])
    total_ident = url + "?" + params_str

    return total_ident.upper()

def get_data_from_api(request_url,service_ident, params_diction, expire_in_days=7):
    ident = create_request_identifier(request_url, params_diction)
    data = get_from_cache(ident,CACHE_DICTION)
    if data:
        if DEBUG:
            print("Loading from data cache: {}... data".format(ident))
    else:
        if DEBUG:
            print("Fetching new data from {}".format(request_url))

        client_key, client_secret, resource_owner_key, resource_owner_secret, verifier = get_tokens_from_service(service_ident)
        oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret,resource_owner_key=resource_owner_key,resource_owner_secret=resource_owner_secret)
        resp = oauth_inst.get(request_url,params=params_diction)
        data_str = resp.text
        data = json.loads(data_str)
        set_in_data_cache(ident, data, expire_in_days)

    return(data)



if __name__ == "__main__":
    if not CLIENT_KEY or not CLIENT_SECRET:
        print("You need to fill in client_key and client_secret in the secret_data.py file.")
        exit()
    if not REQUEST_TOKEN_URL or not BASE_AUTH_URL:
        print("You need to fill in this API's specific OAuth2 URLs in this file.")
        exit()

tumblr_baseurl = "https://api.tumblr.com/v2/tagged"
tumblr_search_params = {"tag":"vegan", "limit":100}

tumblr_res = get_data_from_api(tumblr_baseurl,"Tumblr",tumblr_search_params) # Default expire_in_days


tumblr_res_1=tumblr_res['response'][0]
tumblr_res_2=tumblr_res['response'][0]['blog_name']



def csv_fun1(filename, listname):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Blog Name","Tags","Note_Count"])
        for post in listname['response']:
            post['tags'].sort()
            for post in listname['response']:
                post['note_count']
                writer.writerow([post['blog_name'],post['tags'],post['note_count']])

csv_fun1("Tumblr_Blog.csv",tumblr_res)

def csv_fun2(filename, listname):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Number of Tags","Tag"])
        result_list=[]
        for post in listname['response']:
            for tag in post['tags']:
                result_list.append(tag)
        for tag in result_list:
            tag_count = result_list.count(tag)
            writer.writerow([tag_count, tag])

csv_fun2("Tumblr_Tags.csv", tumblr_res)
####BOOM!!!! DONE##########
