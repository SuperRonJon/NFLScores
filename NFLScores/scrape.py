import json
from match_parsing import get_match_scores


#prints the cores in a readable way for testing purposes
def print_scores(scores):
    for score in scores:
        if score['type'] == 'FG':
            print('{} by {} for {} Yards'.format(score['type'], score['player'], score['yards']))
        elif score['play_type'] == 'run':
            print('{} run by {} for {} Yards'.format(score['type'], score['player'], score['yards']))
        elif score['play_type'] == 'pass':
            print('{} pass from {} to {} for {} Yards'.format(score['type'], score['passer'], score['player'], score['yards']))
        elif score['type'] == 'PAT':
            print('{} good by {}'.format(score['type'], score['player']))
        elif score['type'] == 'SF':
            print('Safety by {}'.format(score['player']))
        else:
            print('{} by {} for {} Yards'.format(score['type'], score['player'], score['yards']))

  
#gets all the score data from the game
scores = get_match_scores(400951597)
#print found scores to console and write to .json file
print_scores(scores)
with open('../stats.json', 'w') as writeJSON:
    json.dump(scores, writeJSON, sort_keys=True, indent=4)