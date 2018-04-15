# Web Crawler for Foxsports to fetch NBA Player Injury Histories
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

# Debug logger
DEBUG = True
def log(msg):
    if DEBUG:
        print(msg)

# Testing Staleness
def is_stale(cache_entry, MAX_STALENESS):
    now = datetime. now().timestamp()
    staleness = now - cache_entry['cache-timestamp']
    return staleness > MAX_STALENESS
    
# Creating Unique Identifier
def uniq_ident(url, params):
    ident_string = url
    for param in params:
        ident_string += ':{}={}'.format(param, params[param])
    return ident_string

# Request with Caching
# I made it so it opens and closes cache within the function so the requests made by nps_test is saved.
def request_with_cache(url, CACHE_DICT, header = {}, params = {}, delay = .5):
    log('------------------------')
    time.sleep(delay)
    uniq_name = uniq_ident(url, params=params)
    try:
        if uniq_name in CACHE_DICT:
            log('Data found in Cache!')
            if is_stale(CACHE_DICT[uniq_name], MAX_STALENESS):
                log('Data in cache is Stale!')
                raise ValueError('Stale Cache!')
            else:
                log('Data is not Stale!')
        else:
            log('Data not found in cache')
            CACHE_DICT[uniq_name]['content'] # To raise appropriate exception
    except:
        log('Requesting Web page...')
        page_text = requests.get(url, params = params, headers=header).text
        log('Caching returned text...')
        CACHE_DICT[uniq_name] = {}
        CACHE_DICT[uniq_name]['content'] = page_text
        CACHE_DICT[uniq_name]['cache-timestamp'] = datetime.now().timestamp()
        log('Caching Complete!')
    finally:
        log('------------------------')
        return CACHE_DICT[uniq_name]['content']

# Function that returns a dictionary with injury data of all nba players
# It is a multi level dictionary: Team --> Player --> Injury
# All tha pages will be cached
def get_nba_player_injuries(CACHE_DICT):
    #### Implement your function here ####
    # Get First Page
    print('Fetching Data...')
    nba_player_injuries = {}
    baseurl = 'https://www.foxsports.com'
    url_addon = '/nba/teams'
    page_soup = BeautifulSoup(request_with_cache(baseurl+url_addon, CACHE_DICT), 'html.parser')
    team_names = [team.text.strip().replace('\n', ' ') for team in page_soup.find_all(class_="wisbb_fullTeamStacked")]
    team_ls = page_soup.find_all("a", href=re.compile("team-roster"))
    counter = 0
    for team in team_ls:
        team_name = team_names[counter]
        nba_player_injuries[team_name] = {}
        counter += 1
        url_addon = team['href']
        page_soup = BeautifulSoup(request_with_cache(baseurl+url_addon, CACHE_DICT), 'html.parser')
        player_ls = page_soup.find_all(class_="wisbb_fullPlayer")
        for player in player_ls:
            full_name = player.find("span").text
            nba_player_injuries[team_name][full_name] = []
            url_addon = player['href'].replace('stats', 'injuries')
            page_soup = BeautifulSoup(request_with_cache(baseurl+url_addon, CACHE_DICT), 'html.parser')
            try:
                injury_table = page_soup.find(class_="wisbb_injuriesTable").find("tbody")
                injuries = injury_table.find_all(class_="wisbb_fvStand")
                print("{} has sustained:".format(full_name))
                for injury in injuries:
                    injury_date = injury.findChildren()[0].text
                    injury_name = injury.findChildren()[1].text
                    injury_dict = {}
                    injury_dict["date"] = injury_date
                    injury_dict["injury"] = injury_name
                    nba_player_injuries[team_name][full_name].append(injury_dict)
                    print(injury_date, injury_name)
            except Exception as e:
                print("{} has not sustained recorded injury.".format(full_name))
    return nba_player_injuries
   
if __name__=="__main__":
    OUTPUT_NAME = 'nba_player_injuries.json'
    CACHE_NAME = 'foxsports_nba_cache.json'
    MAX_STALENESS = 604800 # Have to Refetch Every Week
    try:
        CACHE = open(CACHE_NAME, 'r')
        CACHE_DICT = json.loads(CACHE.read())
        CACHE.close()
    except:
        CACHE_DICT = {}
    returned_dict = get_nba_player_injuries(CACHE_DICT)
    log('------------------------')
    log('Outputting JSON File...')
    OUTPUT = open(OUTPUT_NAME, 'w')
    OUTPUT.write(json.dumps(returned_dict))
    OUTPUT.close()
    log('Output Saved!')
    log('------------------------')
    log('Saving Cache...')
    CACHE = open(CACHE_NAME, 'w')
    CACHE.write(json.dumps(CACHE_DICT))
    CACHE.close()
    log('Cache Saved!')
    log('------------------------')