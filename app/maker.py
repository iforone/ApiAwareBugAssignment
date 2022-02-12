from datetime import datetime

import mysql.connector
import pandas as pd
import pytz
from Profiler import Profiler
import os.path
from DeepProcess import DeepProcessor
from APIScanner import APIScanner
from CodeScanner import CodeScanner
from base import output_folder, ks, exportable_keys


# select which project to check
def project_selector():
    import inquirer
    questions = [
        inquirer.List('project',
                      message="Which project should be selected?",
                      choices=['jdt', 'swt', 'birt', 'eclipse_platform_ui'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['project']


def approach_selector():
    import inquirer
    questions = [
        inquirer.List('approach',
                      message="Select extraction approach?",
                      choices=[
                          'direct - we use top APIs from developers that were assigned to similar bug reports',
                          'indirect - we use top APIs extracted from commits that solved similar bug reports',
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['approach'].split(' - ')[0]


def with_cleaning():
    import inquirer
    questions = [
        inquirer.List('cleaning',
                      message="Should clean the imports? (it cleans up the imports in processed_code table)",
                      choices=['no', 'yes'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['cleaning']


def save_proof_of_work(id_, assignees_, time_, answer_):
    proof = {'bug_id': id_, 'assignees': assignees_, 'report_time': time_}

    ranked_developers = answer[0]
    # check against gold standard and save the result
    for k_ in ks:
        proof['at_' + str(k_)] = 0
        assignees = assignees_.split(',')
        # if assignee was edited we consider the edit too
        for assignee in assignees:
            if assignee in ranked_developers[:k_]:
                proof['at_' + str(k_)] = 1

    # 2 is history
    counter__ = 0
    for x, row_ in answer_[2].head(10).iterrows():
        counter__ += 1
        proof['history_at_' + str(counter__)] = row_['developer']
        proof['history_at_' + str(counter__) + '_v'] = row_['score']

    # 3 is fix
    counter__ = 0
    for x, row_ in answer_[3].head(10).iterrows():
        counter__ += 1
        proof['fix_at_' + str(counter__)] = row_['developer']
        proof['fix_at_' + str(counter__) + '_v'] = row_['score']

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


# connect to a selected database
def mysql_connection(project_name):
    return mysql.connector.connect(
        host='localhost',
        port='32000',
        user='root',
        password='root',
        database=project_name
    )


def make_process_table(builder_):
    builder_.execute('''
    CREATE TABLE IF NOT EXISTS `processed_code` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `file_name` text DEFAULT NULL,
    `commit_hash` char(140) DEFAULT NULL,
    `author` char(140) DEFAULT NULL,
    `username` char(140) DEFAULT NULL,
    `codes` longtext DEFAULT NULL,
    `codes_bag_of_words` longtext DEFAULT NULL,
    `commit_message` text DEFAULT NULL,
    `commit_bag_of_words` text DEFAULT NULL,
    `related_bugs` longtext DEFAULT NULL,
    `packages` text DEFAULT NULL,
    `cleaned_packages` text DEFAULT NULL,
    `used_apis` text DEFAULT NULL,
    `api_usage_details` text DEFAULT NULL,
    `is_extractable` tinyint(1) DEFAULT NULL,
    `committed_at` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `processed_code_id_uindex` (`id`))
    ''')

    try:
        builder.execute('''
        create index processed_code_committed_at_is_extractable_index on processed_code(committed_at, is_extractable);
        ''')
    except:
        pass

    try:
        builder.execute('''
        create index processed_code_commit_hash_index on processed_code(commit_hash);
        ''')
    except:
        pass

    try:
        builder.execute('''
        create index processed_code_author_index on processed_code (author)
        ''')
    except:
        pass


def export_to_csv(data, project_name, extra=''):
    print('☁️ exporting the results to csv')

    tempest = pd.DataFrame.from_dict(data, orient='index')
    tempest[exportable_keys].to_csv('./data/output/' + project_name + '_' + approach + extra + '.csv')


# process the commits to find line-by-line changes and imports of each file
def deep_process(bugs_list, project_name, builder_, db_):
    change_file_name = output_folder + 'lock_' + project_name + '.txt'

    if not os.path.exists(change_file_name):
        print('⚠️ warning: since you miss the main data we are going to recalculate all of it')
        deep_processor = DeepProcessor(project_name, builder_, db_)
        # loop through each bug report
        for index_, bug_ in bugs_list.iterrows():
            deep_processor.update(bug_)
        # lock the deep process
        file = open(change_file_name, "w")
        file.write('locked')
        file.close()
    # else:
    #     deep_processor = DeepProcessor(project_name, builder_, db_)
    #     commits = deep_processor.re_evaluate()
    #     exit(commits)

    print('✅ changes file created / found!')


print('Running maker')
project = project_selector()
approach = approach_selector()

# database work
database = mysql_connection(project)
builder = database.cursor()
make_process_table(builder)
builder.execute("""
    SELECT bug_and_files.*, assginee_mapper.assignees, assginee_mapper.commit_hash, product, component
    FROM bug_and_files
    JOIN (
            SELECT bug_id, GROUP_CONCAT(assignee) as assignees, GROUP_CONCAT(author) as authors, `commit` as commit_hash, product, component
            FROM bug_commit
            group by bug_id
        ) assginee_mapper on assginee_mapper.bug_id = bug_and_files.bug_id

    ORDER BY bug_and_files.report_time
""")#  WHERE authors = assignees

bugs = pd.DataFrame(builder.fetchall())
bugs.columns = builder.column_names

# deeply explore the files
deep_process(bugs, project, builder, database)

# scan the dependencies/ imports and jars
scanner = APIScanner(with_cleaning())
scanner.clean_and_process_imports(project, builder, database)
scanner.update_apis()
scanner.mark_api_usage_in_code(project, builder, database)
scanner.count_used_apis(builder)

# tokenize all codes and commit messages
code_scanner = CodeScanner()
code_scanner.analyze_codes(project, builder, database)

# create profiles for users
profiler = Profiler(approach, project, builder)
# loop through each bug report
counter = 0
response = {}
for index, bug in bugs.iterrows():
    bug['report_time'] = bug['report_time'].tz_localize(pytz.timezone('EST5EDT'))
    bug['report_time'] = bug['report_time'].tz_convert(pytz.timezone('UTC'))
    bug['report_time'] = bug['report_time'].tz_localize(None)

    profiler.sync_profiles(bug)
    answer = profiler.rank_developers(bug)
    ranked_developers = answer[0]

    response[index] = save_proof_of_work(bug['bug_id'], bug['assignees'], bug['report_time'], answer)

    counter += 1
    if counter % 1000 == 0:
        export_to_csv(response, project, '_new' + str(datetime.now().strftime("%d-%b-%Y_%H-%M-%S")))
    print('processed: ' + str(counter) + '/' + str(len(bugs)))

database.close()

# print('📈 Accuracy at:')
# for k in ks:
#     print(str(len(bugs[bugs['at_' + str(k)] == 1])))
#     print('at ' + str(k) + ': ' + str(100 * (len(bugs[bugs['at_' + str(k)] == 1]) / len(bugs))) + '%')

export_to_csv(response, project)
