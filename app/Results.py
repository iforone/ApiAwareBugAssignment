import math

import numpy as np
import pandas as pd
import pytz
from Profiler import Profiler
from base import ks, exportable_keys, LEARN, TEST


def export_to_csv(data, approach, project_name, extra=''):
    print('☁️ exporting the results to csv')

    tempest = pd.DataFrame.from_dict(data, orient='index')
    tempest[exportable_keys].to_csv('./data/output/' + project_name + '_' + approach + extra + '.csv')


def split_data_for_l2r(bugs, experiment, split=10):
    splits = np.array_split(bugs, split)
    chosen_bugs = pd.DataFrame(data=None, columns=bugs.columns)

    # training range
    for training_range in range(0, 5):
        splits[training_range + experiment]['mode_'] = LEARN
        chosen_bugs = chosen_bugs.append(splits[training_range + experiment])

    # testing range
    splits[5 + experiment]['mode_'] = TEST
    chosen_bugs = chosen_bugs.append(splits[5 + experiment])

    return chosen_bugs


def split_data_for_bsba(bugs, threshold):
    counter = 0
    for index, bug in bugs.iterrows():
        mode_ = LEARN
        if len(bugs) - counter <= threshold:
            mode_ = TEST
        bugs.at[index, 'mode_'] = mode_
        counter += 1
    return bugs


def find_response(bugs, project, approach, formula, builder, scanner):
    # 🔥 IDEA 1
    # this is the similar approach to what BSBA used
    # last 600 -> testing
    # the rest -> learning
    if formula == 'similar to BSBA':
        profiler = Profiler(approach, project, builder, scanner.export_all_apis())
        chosen_bugs = split_data_for_bsba(bugs, 600)
        response = do_experiment(chosen_bugs, profiler)
        export_to_csv(response, approach, project)
        return

    # 🧊 IDEA 2
    # this is the similar approach to what L2R and L2R+ used
    # 10-fold
    # 5 experiments  1<= k <= 5
    # training: fold_k -- fold_k+4
    # testing: fold_k+5
    if formula == 'similar to L2R and L2R+':
        for experiment in range(0, 5):
            profiler = Profiler(approach, project, builder, scanner.export_all_apis())
            chosen_bugs = split_data_for_l2r(bugs, experiment, 10)
            # chosen_bugs.to_csv('./data/output/' + project + '_' + str(experiment) + '.csv')
            response = do_experiment(chosen_bugs, profiler)
            export_to_csv(response, approach, project, '_' + str(experiment) + '_')
        return


def do_experiment(bugs_, profiler_):
    response = {}

    for index, bug in bugs_.iterrows():
        mode_ = bug['mode_']
        bug['report_time'] = bug['report_time'].tz_localize(pytz.timezone('EST5EDT'))
        bug['report_time'] = bug['report_time'].tz_convert(pytz.timezone('UTC'))
        bug['report_time'] = bug['report_time'].tz_localize(None)
        bug['bag_of_word_stemmed_split'] = bug['bag_of_word_stemmed'].split()
        profiler_.sync_profiles(bug, mode_)
        if mode_ == TEST:
            response[index] = save_proof_of_work(
                bug['bug_id'],
                bug['assignees'],
                bug['assignees_copy'],
                bug['authors'],
                bug['component'],
                bug['report_time'],
                profiler_.rank_developers(bug),
                mode_
            )
        print('processing: ' + str(bug['bug_id']))

    print('✅ done experimenting')

    return response


def save_proof_of_work(id_, assignees_, assignees_copy_, authors_, c_, time_, answer_, mode_):
    ranked_developers_ = answer_[0]
    proof = {
        'bug_id': id_,
        'component': c_,
        'chosen': answer_[0][0],
        'assignees': assignees_,
        'assignees_copy': assignees_copy_,
        'author': authors_,
        'report_time': time_,
        'mode': mode_,
        'similar_bug': answer_[6],
        'jaccard_score': answer_[7],
        'relevant_apis': answer_[8],
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

    # 4 is code
    counter__ = 0
    for x, row_ in answer_[4].head(10).iterrows():
        counter__ += 1
        proof['code_at_' + str(counter__)] = row_['developer']
        proof['code_at_' + str(counter__) + '_v'] = row_['score']

    # 5 is api
    counter__ = 0
    for x, row_ in answer_[5].head(10).iterrows():
        counter__ += 1
        proof['api_at_' + str(counter__)] = row_['developer']
        proof['api_at_' + str(counter__) + '_v'] = row_['score']

    return proof
