from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re
import json

#Temporary url for testing
my_url = "http://www.espn.com/nfl/playbyplay?gameId=400951580"

#Connecting client and downloading page
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
containers = page_soup.findAll("td", {"class": "game-details"})

#Array to store the scores in
scoring_plays = []

#prints the cores in a readable way for testing purposes
def print_scores(scores):
    for score in scores:
        print("{} by {} for {} Yards".format(score["type"], score["player"], score["yards"]))

#loops through each score and extracts the data
for container in containers:
    new_score = {}
    new_score["type"] = container.findAll("div", {"class": "score-type"})[0].text
    headline = container.findAll("div", {"class": "headline"})[0].text
    new_score["player"] = re.search('^\D+', headline).group(0).strip()
    new_score["yards"] = re.search('\d+\sYd', headline).group(0).split()[0]
    #if the score was a touchdown, extract the Point After Attempt information
    if new_score['type'] == 'TD':
        _ , kick = headline.split('(')
        kick = kick.strip(')')
        kicker, result = kick.rsplit(' ', 1)
        #If the point after attempt is successful, record the kicker that scored as a PAT type
        if result == 'Kick':
            kick_score = {}
            kick_score["type"] = 'PAT'
            kick_score["player"] = kicker
            kick_score["yards"] = 'NA'
            scoring_plays.append(kick_score)
    scoring_plays.append(new_score)

#print found scores to console and write to .json file
print_scores(scoring_plays)
with open("stats.json", "w") as writeJSON:
    json.dump(scoring_plays, writeJSON)