import NFLScores as nfl

year = input('Enter year: ')
weeks = input('Enter all weeks to gather data for: ')
weeks = list(map(int, weeks.split()))
filename = input('Enter filename: ')

for week in weeks:
    scores = nfl.get_week_scores(year, week)
    if weeks.index(week) == 0:
        nfl.write_to_csv(scores, filename)
    else:
        nfl.write_to_csv(scores, filename, append=True)

print('Complete!')
