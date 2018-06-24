import NFLScores as nfl

year = input('Enter year: ')
weeks = input('Enter all weeks to gather data for: ')
weeks = list(map(int, weeks.split()))
file_type = ''
while file_type.lower() != 'csv' and file_type.lower() != 'json':
    file_type = input('Enter file type (csv or json): ')
filename = input('Enter filename: ')

if file_type.lower() == 'csv':
    for week in weeks:
        scores = nfl.get_week_scores(year, week)
        if weeks.index(week) == 0:
            nfl.write_to_csv(scores, filename)
        else:
            nfl.write_to_csv(scores, filename, append=True)
elif file_type.lower() == 'json':
    scores = []
    for week in weeks:
        scores.append(nfl.get_week_scores(year, week))
    nfl.write_to_json(scores, filename)

print('Complete!')
