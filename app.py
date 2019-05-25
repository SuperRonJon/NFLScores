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
        response = jsonify(info['games'])
    else:
        week_data = db.weekdata.find(query, {'games': True})
        games = week_data[0]['games']

    return render_template('week.html', games=games, year=year, week=week)


@app.route('/match')
def game_scores():
    gameid = request.args['id']
    query = {'game_id': gameid}
    if db.gamedata.count_documents(query) == 0:
        games = dict()
        games['game_id'] = gameid
        games['scores'] = nfl.get_match_scores(gameid)
        games['info'] = nfl.get_match_info(gameid)
        db.gamedata.insert_one(games)
    else:
        game_data = db.gamedata.find(query)[0]
        games = {'game_id': game_data['game_id'], 'scores': game_data['scores'], 'info': game_data['info']}

    return render_template('match.html', scores=games)




@app.route('/scores/<year>/<week>/<team>')
def team_week(year, week, team):
    all_scores = nfl.get_week_scores(year, week)
    team_scores = [score for score in all_scores if score['team'] == team]
    response = jsonify(team_scores)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


app.run()
