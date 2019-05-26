import re

from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import NFLScores as nfl

app = Flask(__name__)

client = MongoClient('mongodb://localhost')
db = client.nfls

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/week')
def week_scores():
    year = request.args['year']
    week = request.args['week']

    query = {'week': week, 'year': year}
    if db.weekdata.count_documents(query) == 0:
        info = nfl.get_week_info(year, week)
        db.weekdata.insert_one(info)
        games = info['games']
    else:
        week_data = db.weekdata.find(query, {'games': True})
        games = week_data[0]['games']

    return render_template('week.html', games=games, year=year, week=week)


@app.route('/match')
def game_scores():
    gameid = request.args['id']
    query = {'game_id': gameid}
    if db.gamedata.count_documents(query) == 0:
        game = dict()
        game['game_id'] = gameid
        game['scores'] = nfl.get_match_scores(gameid)
        game['info'] = nfl.get_match_info(gameid)
        db.gamedata.insert_one(game)
    else:
        game_data = db.gamedata.find(query)[0]
        game = {'game_id': game_data['game_id'], 'scores': game_data['scores'], 'info': game_data['info']}
    
    plays = list()
    for play in game['scores']:
        plays.append(make_string(play))
    game['scores'] = plays
    print(game)

    return render_template('match.html', game=game)


def make_string(play):
    result = ''
    score = re.search(r'\d+\-\d+', play['score']).group(0)
    result += '({}) '.format(play['team'].upper())
    if play['type'] == 'TD':
        if play['play_type'] == 'pass':
            result += 'Pass from {} to {} for {} yards'.format(play['passer'], play['player'], play['yards'])
        elif play['play_type'] == 'run':
            result += 'Run by {} for {} yards'.format(play['player'], play['yards'])
        else:
            result += '{} by {} for {} yards'.format(play['play_type'], play['player'], play['yards'])
    elif play['type'] == 'PAT':
        result += 'Point after good by {}'.format(play['player'])
    elif play['type'] == 'FG':
        result += 'Field goal good by {} for {} yards'.format(play['player'], play['yards'])
    elif play['type'] == '2PtConv':
        if play['play_type'] == 'pass':
            result += 'Two point conversion pass from {} to {}'.format(play['passer'], play['player'])
        elif play['play_type'] == 'run':
            result += 'Two point conversion run by {}'.format(play['player'])
    elif play['type'] == 'SF':
        result += 'Safety by {}'.format(play['player'])
    return result + " " + score

app.run()
