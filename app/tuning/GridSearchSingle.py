# The task here is to find the history, code and api weights using grid search
import pandas as pd
import numpy as np
import math
import statistics
from pandas import Timestamp
import math

# range of the tuning for each of the 3 parameters
parameter_range = [0, 0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.75, 0.8, 0.9, 0.99, 0.999, 1]
# file name:
file = '../../data/output/jdt_direct-best-base-and-best-mapper.csv'
# project name:
project = 'jdt'
# approach of the api
approach = 'ml'


# get stat for -old or new and then compare
def get_stat_for(file_, style_, time_a=1, time_b=1, time_c=1):
    df = pd.read_csv(file_)

    count = 0
    total = 0
    for (index, row) in df.iterrows():
        total_scores = {'history': 0, 'api': 0, 'code': 0, 'api_s': 0}
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
                if str(h) == 'nan' or h == 0 or total_scores['history'] <= 0:
                    scores[h_developer] = scores.get(h_developer, []) + [0]
                else:
                    scores[h_developer] = scores.get(h_developer, []) + [
                        time_a * float(h * 100 / total_scores['history'])]

            if str(c_developer) != 'nan':
                if str(c) == 'nan' or c == 0 or total_scores['code'] <= 0:
                    scores[c_developer] = scores.get(c_developer, []) + [0]
                else:
                    scores[c_developer] = scores.get(c_developer, []) + [time_b * float(c * 100 / total_scores['code'])]

            if str(a_developer) != 'nan':
                if str(a) == 'nan' or a == 0 or total_scores['api'] <= 0:
                    scores[a_developer] = scores.get(a_developer, []) + [0]
                else:
                    x = None
                    if style_ == 'only-bsba':
                        x = 0
                    if style == 'confidence':
                        x = row['jaccard_score']
                    if style == 'without-confidence':
                        x = 1
                    if style == 'descending-confidence':
                        row['jaccard_score'] = row['jaccard_score'] * 2 / i
                        x = row['jaccard_score']

                    scores[a_developer] = scores.get(a_developer, []) + [
                        time_c * x * float(a * 100 / total_scores['api'])]
                    pass

        # calculate the total
        for index_, score in scores.items():
            if len(score) == 0:
                scores[index_] = 0
            else:
                scores[index_] = sum(score)

        sort = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        chosen = ''
        if len(sort) != 0:
            chosen = sort[0][0]
        if chosen == row['assignees']:
            count += 1
        total += 1

    return count / total


for style in ['only-bsba', 'confidence', 'without-confidence', 'descending-confidence']:
    # do the grid search
    answer = {}

    for history_score in parameter_range:
        for code_score in parameter_range:
            if style == 'only-bsba':
                key = str(history_score) + '_' + str(code_score) + '_' + str(0)
                value = get_stat_for(file, style, history_score, code_score, 0)
                print(key + "==" + str(value))
                answer[key] = value
            else:
                for api_score in parameter_range:
                    key = str(history_score) + '_' + str(code_score) + '_' + str(api_score)
                    value = get_stat_for(file, style, history_score, code_score, api_score)
                    print(key + "==" + str(value))
                    answer[key] = value

    # output the results
    f = open('../../data/output/tuning/' + project + "_" + approach + "_" + style + ".txt", "w")
    for k in answer.keys():
        f.write("{}:{}\n".format(k, answer[k]))
    f.close()
