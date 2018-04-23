from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re
import json

#Temporary url for testing
my_url = "http://www.espn.com/nfl/game?gameId=400951597"

#Connecting client and downloading page
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
containers = page_soup.findAll("td", {"class": "game-details"})


#prints the cores in a readable way for testing purposes
def print_scores(scores):
    for score in scores:
        if score["type"] == "FG":
            print("{} by {} for {} Yards".format(score["type"], score["player"], score["yards"]))
        elif score["play_type"] == "run":
            print("{} run by {} for {} Yards".format(score["type"], score["player"], score["yards"]))
        elif score["play_type"] == "pass":
            print("{} pass from {} to {} for {} Yards".format(score["type"], score["passer"], score["player"], score["yards"]))
        elif score["type"] == "PAT":
            print("{} good by {}".format(score["type"], score["player"]))
        elif score["type"] == "SF":
            print("Safety by {}".format(score["player"]))
        else:
            print("{} by {} for {} Yards".format(score["type"], score["player"], score["yards"]))


#retrieves all the scoring plays from a single match
#returns a list of objects containing the plays data
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
    new_score["type"] = container.findAll("div", {"class": "score-type"})[0].text
    headline = container.findAll("div", {"class": "headline"})[0].text
    if headline[-1] != ")":
        no_kick = True
    if new_score["type"] != "SF":
        new_score["player"] = re.search('^\D+', headline).group(0).strip()
        new_score["yards"] = re.search('\d+\sYd', headline).group(0).split()[0]
    else:
        new_score["player"] = re.search('\D+?(?=\sSafety)',headline).group(0)
        new_score["yards"] = "NA"
    #if the score was a touchdown, extract extra information
    if new_score['type'] == 'TD':
        #gets whether the TD was a run/pass
        if not no_kick:
            new_score["play_type"] = re.search('Yd\s(\w*)\s', headline).group(1).lower()
        else:
            new_score["play_type"] = re.search('Yd\s(\w*)$', headline).group(1).lower()
        #if the touchdown was a pass, get the passer information
        if new_score["play_type"] == "pass":
            #extract passer information
            if not no_kick:
                new_score["passer"] = re.search('from\s(\D*)\s\(', headline).group(1)
            else:
                new_score["passer"] = re.search('from\s(\D*)$', headline).group(1)
        else:
            new_score["passer"] = "NA"
        if not no_kick:
            _ , kick = headline.split('(')
            kick = kick.strip(')')
            kicker, result = kick.rsplit(' ', 1)
            #If the point after attempt is successful, record the kicker that scored as a PAT type
            if result == 'Kick':
                kick_score = {}
                kick_score["type"] = 'PAT'
                kick_score["player"] = kicker
                kick_score["yards"] = 'NA'
                kick_score["play_type"] = "PAT"
                scores.append(kick_score)
    else:
        new_score["play_type"] = new_score["type"]
        new_score["passer"] = "NA"
    scores.append(new_score)
    return scores
  
#gets all the score data from the game
scoring_plays = retrieve_data(containers)
#print found scores to console and write to .json file
print_scores(scoring_plays)
with open("stats.json", "w") as writeJSON:
    json.dump(scoring_plays, writeJSON, sort_keys=True, indent=4)