# this file is to check and verify and report the result of the whole Bug Assignment:
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
df = pd.read_csv('./data/output/jdt_direct-fluid-profile.csv')

count = 0
total = 0
previous = ''
for index, row in df.iterrows():
    total_scores = {'history': 0, 'api': 0, 'code': 0}
    for i in range(1, 11):
        h = row['history_at_' + str(i) + '_v']
        c = row['code_at_' + str(i) + '_v']
        a = row['api_at_' + str(i) + '_v']
        if str(h) != 'nan':
            total_scores['history'] += h
        if str(c) != 'nan':
            total_scores['code'] += c
        if str(a) != 'nan':
            total_scores['api'] += a


    scores = {}
    for i in range(1, 11):
        h = row['history_at_' + str(i) + '_v']
        h_developer = row['history_at_' + str(i)]
        c = row['code_at_' + str(i) + '_v']
        c_developer = row['code_at_' + str(i)]
        a = row['api_at_' + str(i) + '_v']
        a_developer = row['api_at_' + str(i)]

        if str(h_developer) != 'nan':
            if str(h) == 'nan' or total_scores['history'] <= 0:
                scores[h_developer] = scores.get(h_developer, 0) + 0
            else:
                scores[h_developer] = scores.get(h_developer, 0) + (h * 100 / total_scores['history'])

        if str(c_developer) != 'nan':
            if str(c) == 'nan' or total_scores['code'] <= 0:
                scores[c_developer] = scores.get(c_developer, 0) + 0
            else:
                scores[c_developer] = scores.get(c_developer, 0) + (c * 100 / total_scores['code'])

        if str(a_developer) != 'nan':
            if str(a) == 'nan' or total_scores['api'] <= 0:
                scores[a_developer] = scores.get(a_developer, 0) + 0
            else:
                scores[a_developer] = scores.get(a_developer, 0) + (a * 100 / total_scores['api'])

    # sorting the results
    sort = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    if sort[0][0] == row['assignees']:
        count += 1

    previous = row['assignees']
    total += 1

print(count)
print(count / total)
