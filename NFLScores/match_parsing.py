from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re
import requests


def get_match_containers(gameId):
    #connecting to client and downloading page information
    match_url = 'http://www.espn.com/nfl/game?gameId=' + str(gameId)
    uClient = uReq(match_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')
    containers = page_soup.findAll('td', {'class': 'game-details'})
    return containers


#retrieves all the scoring plays from a single match
#returns a list of objects containing the html plays data
def retrieve_data(containers):
    scoring_plays = []
    for container in containers:
        new_scores = parse_play(container)
        scoring_plays.extend(new_scores)
    return scoring_plays


#parses the data from one scoring play
#returns a list of plays obtained from a single score (e.g. a Touchdown + an Extra Point)
def parse_play(container):
    scores = []
    new_score = {}
    no_kick = False
    new_score['type'] = container.findAll('div', {'class': 'score-type'})[0].text
    headline = container.findAll('div', {'class': 'headline'})[0].text
    if headline[-1] != ')':
        no_kick = True
    if new_score['type'] != 'SF':
        new_score['player'] = re.search('^\D+', headline).group(0).strip()
        new_score['yards'] = re.search('\d+\sYd', headline).group(0).split()[0]
    else:
        new_score['player'] = re.search('\D+?(?=\sSafety)',headline).group(0)
        new_score['yards'] = 'NA'
    #if the score was a touchdown, extract extra information
    if new_score['type'] == 'TD':
        #gets whether the TD was a run/pass
        if not no_kick:
            new_score['play_type'] = re.search('Yd\s(\w*)\s', headline).group(1).lower()
        else:
            new_score['play_type'] = re.search('Yd\s(\w*)$', headline).group(1).lower()
        #if the touchdown was a pass, get the passer information
        if new_score['play_type'] == 'pass':
            #extract passer information
            if not no_kick:
                new_score['passer'] = re.search('from\s(\D*)\s\(', headline).group(1)
            else:
                new_score['passer'] = re.search('from\s(\D*)$', headline).group(1)
        else:
            new_score['passer'] = 'NA'
        if not no_kick:
            _ , kick = headline.split('(')
            kick = kick.strip(')')
            kicker, result = kick.rsplit(' ', 1)
            #If the point after attempt is successful, record the kicker that scored as a PAT type
            if result == 'Kick':
                kick_score = {}
                kick_score['passer'] = 'NA'
                kick_score['type'] = 'PAT'
                kick_score['player'] = kicker
                kick_score['yards'] = 'NA'
                kick_score['play_type'] = 'PAT'
                scores.append(kick_score)
    else:
        new_score['play_type'] = new_score['type']
        new_score['passer'] = 'NA'
    scores.append(new_score)
    return scores


def get_match_scores(gameId):
    scoring_plays = retrieve_data(get_match_containers(gameId))
    return scoring_plays


#gets all match ids from a specified NFL week via espn APIs
def get_match_ids(year, week):
    id_url = 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?lang=en&region=us&calendartype=blacklist&limit=100&dates=' + str(year) + '&seasontype=2&week=' + str(week) 
    response = requests.get(id_url)
    data = response.json()
    gameIds = []
    for event in data['events']:
        gameIds.append(event['id'])
    return gameIds


#gets all scoring plays from an entire week of NFL games
def get_week_scores(year, week):
    ids = get_match_ids(year, week)
    scoring_plays = []
    for id in ids:
        scoring_plays.extend(get_match_scores(id))
    
    return scoring_plays
