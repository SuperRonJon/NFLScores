from flask import Flask, jsonify
import NFLScores as nfl

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world!'

@app.route('/scores/<year>/<week>')
def week_scores(year, week):
    scores = nfl.get_week_scores(year, week)
    return jsonify(scores)


@app.route('/scores/<year>/<week>/<team>')
def team_week(year, week, team):
    all_scores = nfl.get_week_scores(year, week)
    team_scores = [score for score in all_scores if score['team'] == team]
    return jsonify(team_scores)
