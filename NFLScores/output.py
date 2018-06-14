import json


# prints the cores in a readable way for testing purposes
def print_scores(scores):
    for score in scores:
        if score['type'] == 'FG':
            print('{} by {} for {} Yards'.format(score['type'], score['player'], score['yards']))
        elif score['play_type'] == 'run':
            print('{} run by {} for {} Yards'.format(score['type'], score['player'], score['yards']))
        elif score['play_type'] == 'pass':
            print('{} pass from {} to {} for {} Yards'.format(score['type'], score['passer'], score['player'],
                                                              score['yards']))
        elif score['type'] == 'PAT':
            print('{} good by {}'.format(score['type'], score['player']))
        elif score['type'] == 'SF':
            print('Safety by {}'.format(score['player']))
        elif score['type'] == '2PtConv':
            print('Conversion by {}'.format(score['player']))
        else:
            print('{} by {} for {} Yards'.format(score['type'], score['player'], score['yards']))


def write_to_json(scores, filename):
    with open(filename, 'w') as writeJSON:
        json.dump(scores, writeJSON, sort_keys=True, indent=4)


def write_to_csv(scores, filename, append=False):
    if append:
        f = open(filename, 'a')
    else:
        f = open(filename, 'w')

    if not append:
        headers = "team, player, type, yards, play type, passer, score\n"
        f.write(headers)
    for score in scores:
        f.write(score["team"] + "," + score["player"] + "," + score["type"] + "," + score["yards"] + "," + score[
            "play_type"] + "," + score["passer"] + "," + score["score"] + "\n")
    f.close()
