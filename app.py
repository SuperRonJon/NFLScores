from flask import Flask, jsonify, request
from pymongo import MongoClient
import NFLScores as nfl

app = Flask(__name__)

client = MongoClient('mongodb://localhost')
db = client.nfls

@app.route('/add', methods=["POST"])
def add_user():
    to_add = {'name': request.form['name'], 'phone': request.form['phone']}
    print(f'Adding {request.form["name"]}, {request.form["phone"]}')
    db.collections.insert_one(to_add)
    return 'ok'

@app.route('/')
def index():
    return 'Hello world!'

@app.route('/scores/<year>/<week>')
def week_scores(year, week):
    query = {'week': week, 'year': year}
    if db.weekdata.count_documents(query) == 0:
        info = nfl.get_week_info(year, week)
        db.weekdata.insert_one(info)
        response = jsonify(info['games'])
    else:
        week_data = db.weekdata.find(query, {'games': True})
        response = jsonify(week_data[0]['games'])

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/scores/<gameid>')
def game_scores(gameid):
    query = {'game_id': gameid}
    if db.gamedata.count_documents(query) == 0:
        print('From scrape')
        games = dict()
        games['game_id'] = gameid
        games['scores'] = nfl.get_match_scores(gameid)
        games['info'] = nfl.get_match_info(gameid)
        response = jsonify(games)
        db.gamedata.insert_one(games)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        print('from db')
        game_data = db.gamedata.find(query)[0]
        res_data = {'game_id': game_data['game_id'], 'scores': game_data['scores'], 'info': game_data['info']}
        response = jsonify(res_data)

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




@app.route('/scores/<year>/<week>/<team>')
def team_week(year, week, team):
    all_scores = nfl.get_week_scores(year, week)
    team_scores = [score for score in all_scores if score['team'] == team]
    response = jsonify(team_scores)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


app.run()
