import re
import os

from flask import Flask, jsonify, request, render_template, redirect
from pymongo import MongoClient
import NFLScores as nfl

app = Flask(__name__)

try:
    mongo_uri = os.environ['MONGODB_URI']
except KeyError:
    from secrets import mongoURI
    mongo_uri = mongoURI

client = MongoClient(mongo_uri)
db = client.nfls


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/week')
def week_matches():
    try:
        year = request.args['year']
        week = request.args['week']
    except:
        return render_template('notfound.html', title='Whoops...')

    try:
        playoffs = request.args['playoffs']
    except:
        playoffs = "off"
    
    if playoffs == "on":
        seasontype = 3
    else:
        seasontype = 2

    title = '{} Week {}'.format(year, week)

    query = {'week': week, 'year': year, 'seasontype': seasontype}
    if db.weekdata.count_documents(query) == 0:
        info = nfl.get_week_info(year, week, seasontype)
        db.weekdata.insert_one(info)
        games = info['games']
    else:
        week_data = db.weekdata.find(query, {'games': True})
        games = week_data[0]['games']
    
    return render_template('week.html', games=games, year=year, week=week, playoffs=playoffs, title=title)


@app.route('/update_week/<year>/<week>/<playoffs>', methods=['POST'])
def update_week(year, week, playoffs):
    redirect_link = "/week?year={}&week={}".format(year, week)
    if playoffs == "on":
        seasontype = 3
        redirect_link += "&playoffs=on"
    else:
        seasontype = 2
    query = {'year': year, 'week': week, 'seasontype': seasontype}
    db.weekdata.delete_many(query)

    info = nfl.get_week_info(year, week, seasontype)
    db.weekdata.insert_one(info)

    return redirect(redirect_link)


@app.route('/match')
def game_scores():
    try:
        gameid = request.args['gameid']
    except:
        return render_template('notfound.html', title='Whoops...')
    query = {'game_id': gameid}
    if db.gamedata.count_documents(query) == 0:
        game = dict()
        game['game_id'] = gameid
        try:
            game['scores'] = nfl.get_match_scores(gameid)
        except Exception as err:
            print("Exception getting scores:", err)
            return render_template('notfound.html', title='Whoops...')
        try:
            game['info'] = nfl.get_match_info(gameid)
        except ValueError:
            return render_template('notfound.html', title='Whoops...')
        db.gamedata.insert_one(game)
    else:
        game_data = db.gamedata.find(query)[0]
        game = {'game_id': game_data['game_id'], 'scores': game_data['scores'], 'info': game_data['info']}

    plays = list()
    for play in game['scores']:
        plays.append(make_string(play))
    game['scores'] = plays
    title = '{} vs {}'.format(game['info']['team1'], game['info']['team2'])

    return render_template('match.html', game=game, title=title)


@app.route('/update_match/<gameid>', methods=['POST'])
def update_match(gameid):
    if request.method == 'POST':
        query = {'game_id': str(gameid)}
        db.gamedata.delete_many(query)

        game = dict()
        game['game_id'] = gameid
        game['scores'] = nfl.get_match_scores(gameid)
        try:
            game['info'] = nfl.get_match_info(gameid)
        except ValueError:
            pass
        db.gamedata.insert_one(game)

        return redirect('/match?gameid=' + str(gameid))


@app.route('/full_week')
def week_scores():
    try:
        year = request.args['year']
        week = request.args['week']
        playoffs = request.args['playoffs']
    except:
        return render_template('notfound.html', title='Whoops...')

    if playoffs == "on":
        seasontype = 3
    else:
        seasontype = 2

    query = {'week': week, 'year': year, 'seasontype': seasontype}
    if db.fullweek.count_documents(query) == 0:
        try:
            week_data = nfl.get_full_week_data(year, week, seasontype)
        except:
            return render_template('notfound.html', title='Whoops...')
        response = week_data
        db.fullweek.insert_one(week_data)
    else:
        week_data = db.fullweek.find(query)[0]
        response = {'games': week_data['games'], 'year': week_data['year'], 'week': week_data['week']}
    
    for game in response['games']:
        for play in game['plays']:
            play['play_string'] = make_string(play)
    
    if playoffs == "on":
        title = "Playoffs {} week {}".format(year, week)
    else:
        title = "{} week {}".format(year, week)
            
    return render_template('full_week.html', data=response, playoffs=playoffs, title=title)


@app.route('/update_full_week/<year>/<week>/<playoffs>', methods=['POST'])
def update_full_week(year, week, playoffs):
    redirect_link = '/full_week?year={}&week={}'.format(year, week)
    if playoffs == "on":
        seasontype = 3
        redirect_link += "&playoffs=on"
    else:
        seasontype = 2
        redirect_link += "&playoffs=off"

    if request.method == 'POST':
        query = {'week': week, 'year': year, 'seasontype': seasontype}
        db.fullweek.delete_many(query)

        week_data = nfl.get_full_week_data(year, week, seasontype)
        db.fullweek.insert_one(week_data)

        return redirect(redirect_link)


def make_string(play):
    result = ''
    score = re.search(r'\d+\-\d+', play['score']).group(0)
    result += '({}) '.format(play['team'])
    if play['type'] == 'TD':
        if play['play_type'] == 'pass':
            result += 'Pass from {} to {} for {} yards'.format(play['passer'], play['player'], play['yards'])
        elif play['play_type'] == 'run':
            result += 'Run by {} for {} yards'.format(play['player'], play['yards'])
        else:
            if play['yards'] == 'NA':
                result += '{} by {} in the End Zone'.format(play['play_type'], play['player'])
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


if __name__ == '__main__':
    PORT = None
    try:
        PORT = os.environ['PORT']
    except KeyError:
        PORT = 8080
    app.run(host='0.0.0.0', port=PORT)
