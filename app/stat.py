# this file is to check and verify and report the result of the whole Bug Assignment:
import pandas as pd
import numpy as np


def get_stat_for(file, authors, label='-new'):
    pd.set_option("display.max_columns", None)
    df = pd.read_csv(file)
    count = 0
    total = 0
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

        # golds = {row['history_at_1']: 0, row['history_at_2']: 0}
        # for name, score in scores.items():
        #     if name in golds:
        #         golds[name] = golds.get(name, 0) + score
        # sort = sorted(golds.items(), key=lambda x: x[1], reverse=True)
        # if sort[0][0] == row['assignees']:
        #     count +=1

        previous = row['assignees']
        total += 1

        if row['assignees'] not in authors:
            authors[row['assignees']] = {
                'total-new': 0, 'count_differently-new': 0, 'count-new': 0, 'count_history-new': 0, 'count_code-new': 0, 'count_api-new': 0,
                'total-old': 0, 'count_differently-old': 0, 'count-old': 0, 'count_history-old': 0, 'count_code-old': 0, 'count_api-old': 0,
                }

        authors[row['assignees']]['total' + label] += 1
        if row['assignees'] == row['history_at_1']:
            authors[row['assignees']]['count_history' + label] += 1
        if row['assignees'] == row['code_at_1']:
            authors[row['assignees']]['count_code' + label] += 1
        if row['assignees'] == row['api_at_1']:
            authors[row['assignees']]['count_api' + label] += 1
        if 1 == row['at_1']:
            authors[row['assignees']]['count' + label] += 1
        if sort[0][0] == row['assignees']:
            authors[row['assignees']]['count_differently' + label] += 1

    print(label)
    print(count)
    print(count / total)
    return authors


authors_ = {}
authors_ = get_stat_for('./data/output/jdt_direct.csv', authors_, '-new')
authors_ = get_stat_for('./data/output/jdt_direct-with-day-distance.csv', authors_, '-old')

for name, author in authors_.items():
    if name not in ['Adam Kiezun', 'Andrew Eisenberg', 'Benno Baumgartner', 'Björn Michael', 'Christof Marti', 'Dani Megert', 'Darin Swanson', 'Darin Wright', 'Deepak Azad', 'Dirk Baeumer', 'Erich Gamma', 'Jared Burns', 'Lars Vogel', 'Manju Mathew', 'Marcel Bruch', 'Markus Keller', 'Martin Aeschlimann', 'Moshe WAJNBERG', 'Nikolay Metchev', 'Noopur Gupta', 'Paul Fullbright', 'Paul Webster', 'Philipe Mulet', 'Philippe Marschall', 'Rabea Gransberger', 'Raksha Vasisht', 'Samrat Dhillon', 'Snjezana Peco', 'Stephan Herrmann', 'Szymon Ptaszkiewicz', 'Tobias Widmer', 'Tom Hofmann']:
        continue
    author['count_differently-change'] = author['count_differently-new'] - author['count_differently-old']
    author['count-change'] = author['count-new'] - author['count-old']
    author['history-change'] = author['count_history-new'] - author['count_history-old']
    author['code-change'] = author['count_code-new'] - author['count_code-old']
    author['api-change'] = author['count_api-new'] - author['count_api-old']


authors_

