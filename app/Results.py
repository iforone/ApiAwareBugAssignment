import pandas as pd
import pytz
from base import ks, exportable_keys, LEARN, TEST
from datetime import datetime


def export_to_csv(data, approach, project_name, extra=''):
    print('☁️ exporting the results to csv')

    tempest = pd.DataFrame.from_dict(data, orient='index')
    tempest[exportable_keys].to_csv('./data/output/' + project_name + '_' + approach + extra + '.csv')


def find_response(profiler, bugs, project, approach, formula):
    response = {}

    # 🔥 IDEA 1
    # this is the similar approach to what BSBA used
    # last 600 -> testing
    # the rest -> learning
    if formula == 'similar to BSBA':
        counter = 0
        test_threshold = 600
        for index, bug in bugs.iterrows():
            mode_ = LEARN
            if len(bugs) - counter <= test_threshold:
                mode_ = TEST

            bug['report_time'] = bug['report_time'].tz_localize(pytz.timezone('EST5EDT'))
            bug['report_time'] = bug['report_time'].tz_convert(pytz.timezone('UTC'))
            bug['report_time'] = bug['report_time'].tz_localize(None)

            profiler.sync_profiles(bug, mode_)
            answer = profiler.rank_developers(bug)

            response[index] = save_proof_of_work(
                bug['bug_id'],
                bug['assignees'],
                bug['authors'],
                bug['component'],
                bug['report_time'],
                answer,
                mode_
            )

            counter += 1
            if counter % 1000 == 0:
                export_to_csv(response, approach, project, '_new' + str(datetime.now().strftime("%d-%b-%Y_%H-%M-%S")))
            print('processed: ' + str(counter) + '/' + str(len(bugs)))

    return response


def save_proof_of_work(id_, assignees_, authors_, c_, time_, answer_, mode_):
    ranked_developers_ = answer_[0]
    proof = {
        'bug_id': id_,
        'component': c_,
        'chosen': answer_[0][0],
        'assignees': assignees_,
        'author': authors_,
        'report_time': time_,
        'mode': mode_,
    }

    # check against gold standard and save the result
    for k_ in ks:
        proof['at_' + str(k_)] = 0
        assignees = assignees_.split(',')
        # if assignee was edited we consider the edit too
        for assignee in assignees:
            if assignee in ranked_developers_[:k_]:
                proof['at_' + str(k_)] = 1

    # 2 is history
    counter__ = 0
    for x, row_ in answer_[2].head(10).iterrows():
        counter__ += 1
        proof['history_at_' + str(counter__)] = row_['developer']
        proof['history_at_' + str(counter__) + '_v'] = row_['score']

    # 3 is code
    counter__ = 0
    for x, row_ in answer_[3].head(10).iterrows():
        counter__ += 1
        proof['code_at_' + str(counter__)] = row_['developer']
        proof['code_at_' + str(counter__) + '_v'] = row_['score']

    # 4 is api
    counter__ = 0
    for x, row_ in answer_[4].head(10).iterrows():
        counter__ += 1
        proof['api_at_' + str(counter__)] = row_['developer']
        proof['api_at_' + str(counter__) + '_v'] = row_['score']

    return proof
