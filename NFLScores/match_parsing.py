from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re
import requests

#get all the containers on the page that include information on each score
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
    no_yards = False
    new_score['type'] = container.findAll('div', {'class': 'score-type'})[0].text
    new_score['score'] = '= "' + get_game_score(container) + '"'
    new_score['team'] = get_team_name(container)
    headline = container.findAll('div', {'class': 'headline'})[0].text
    if headline[-1] != ')':
        no_kick = True
    if new_score['type'] != 'SF':
        player_result = re.search('^(\D+)(?:\d|Interception|Fumble|Defensive)', headline)
        #if the play was an interception or fumble in the endzone there are no yards
        if player_result.group(0).split()[-1] == 'Interception' or player_result.group(0).split()[-1] == 'Fumble':
            new_score['yards'] = 'NA'
            no_yards = True
            no_yards_type = player_result.group(0).split()[-1].lower()
        elif player_result.group(0).split()[-1] == 'Defensive':
            new_score['yards'] = 'NA'
            no_yards = True
        else:
            new_score['yards'] = re.search('\d+\sYd', headline).group(0).split()[0]
        new_score['player'] = player_result.group(1).strip()
    else:
        new_score['player'] = new_score['team'].upper() + " DEFENSE" #re.search('\D+?(?=\sSafety)',headline, re.IGNORECASE).group(0)
        new_score['yards'] = 'NA'
    #if the score was a touchdown, extract extra information
    if new_score['type'] == 'TD':
        #gets whether the TD was a run/pass
        if no_yards:
            new_score['play_type'] = no_yards_type
        elif not no_kick:
            new_score['play_type'] = re.search('Yd\s(\w*)\s', headline).group(1).lower()
        else:
            new_score['play_type'] = re.search('Yd\s(\w*)', headline).group(1).lower()
        #if the touchdown was a pass, get the passer information
        if new_score['play_type'] == 'pass':
            #extract passer information
            if not no_kick:
                new_score['passer'] = re.search('from\s(\D*)\s\(', headline).group(1)
            else:
                new_score['passer'] = re.search('from\s(\D*)$', headline).group(1)
        else:
            new_score['passer'] = 'NA'
        #add extra information to other touchdown types
        if new_score['play_type'] != 'run' and new_score['play_type'] != 'pass':
            new_score['play_type'] += ' return'
        if not no_kick:
            point_after = get_point_after(headline, new_score['team'], new_score['score'])
            if point_after is not None:
                scores.append(point_after)
    else:
        new_score['play_type'] = new_score['type']
        new_score['passer'] = 'NA'
    scores.append(new_score)
    return scores


#checks whether or not the kick was successful, if th
def get_point_after(headline, team, score):
    _ , kick = headline.split('(')
    kick = kick.strip(')')
    kicker, result = kick.rsplit(' ', 1)
    #if the point after is a successful kick, record that score
    if result == 'Kick':
        kick_score = {}
        kick_score['team'] = team
        kick_score['score'] = score
        kick_score['passer'] = 'NA'
        kick_score['type'] = 'PAT'
        kick_score['player'] = kicker
        kick_score['yards'] = 'NA'
        kick_score['play_type'] = 'PAT'
        return kick_score
    #if the point after is a successful 2 point conversion, record that score
    elif result == 'Conversion':
        conversion_score = {}
        conversion_score['team'] = team
        conversion_score['score'] = score
        conversion_score['type'] = '2PtConv'
        conversion_score['yards'] = 'NA'
        player1 = re.search('(\D+)(?:Run|Pass)', kick).group(1).strip()
        player_removed = kick[len(player1):].strip()
        conversion_score['play_type'] = player_removed.split(' ', 1)[0].lower()
        #if the conversion attempt was a passing play, figure out the passer and reciever
        if conversion_score['play_type'] == 'pass':
            conversion_score['passer'] = player1
            conversion_score['player'] = re.search('to\s(\D+)\sfor',kick).group(1)
        #if it was a run, there is no passer
        else:
            conversion_score['passer'] = 'NA'
            conversion_score['player'] = player1
        return conversion_score
    else:
        return None


#parses the game score after the current scoring play from the container
#returns a string containing the score format "{Home Team}-{Away Team}"
def get_game_score(container):
    score1_container = container.next_sibling
    score1 = score1_container.text
    score2_container = score1_container.next_sibling
    score2 = score2_container.text
    return score1 + '-' + score2


#parses the abbreviation for the scoring team's name from the container
#returns a string containing the scoring team's abbreviation, ex 'jax'
def get_team_name(container):
    url = container.previous_sibling.img['src']
    abbreviation = re.search('\/500\/(\D+).png', url).group(1)
    return abbreviation


#returns a list of all the scoring plays in one match specified by the ESPN gameid
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
