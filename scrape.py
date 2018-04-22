from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re

my_url = "http://www.espn.com/nfl/playbyplay?gameId=400951580"

uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
containers = page_soup.findAll("td", {"class": "game-details"})

scoring_plays = []


for container in containers:
    new_score = {}
    new_score["type"] = container.findAll("div", {"class": "score-type"})[0].text
    headline = container.findAll("div", {"class": "headline"})[0].text
    new_score["player"] = re.search('^\D+', headline).group(0).strip()
    new_score["yards"] = re.search('\d+\sYd', headline).group(0).split()[0]

    print(new_score)