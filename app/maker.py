import mysql.connector
import pandas as pd
from Profiler import Profiler

ks = [1, 2, 3, 4, 5, 10]


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


# connect to a selected database
def mysql_connection(project_name):
    return mysql.connector.connect(
        host='localhost',
        port='32000',
        user='root',
        password='root',
        database=project_name
    )


def export_to_csv(data, project_name):
    print('exporting the results to csv')
    keys = ['bug_id', 'at_1', 'at_2', 'at_3', 'at_4', 'at_5', 'at_10']
    data[keys].to_csv('./data/output/' + project_name + '_' + approach + '.csv')


print('Running maker')

project = project_selector()
approach = approach_selector()
database = mysql_connection(project)

# get all bugs for the project
builder = database.cursor()
builder.execute("""
    SELECT bug_and_files.*, assginee_mapper.assignees
    FROM bug_and_files
    JOIN (
            SELECT bug_id, GROUP_CONCAT(assignee) as assignees
            FROM bug_commit
            group by bug_id
        ) assginee_mapper on assginee_mapper.bug_id = bug_and_files.bug_id
    ORDER BY bug_and_files.report_time
""")

result = pd.DataFrame(builder.fetchall())
result.columns = builder.column_names
database.close()

print(result)

profiler = Profiler(approach, project)
# loop through each bug report
for index, bug in result.iterrows():
    # run 3 modules
    profiler.sync_history(bug)
    #profiler.sync_activity(bug)
    profiler.sync_api(bug)

    # calculate ranking
    ranked_developers = profiler.rank_developers()

    # check against gold standard and save the result
    for k in ks:
        result.at[index, 'at_' + str(k)] = 0

        # if assignee was edited we consider the edit too
        assignees = bug['assignees'].split(',')
        for assignee in assignees:
            if assignee in ranked_developers[:k]:
                result.at[index, 'at_' + str(k)] = 1

export_to_csv(result, project)

