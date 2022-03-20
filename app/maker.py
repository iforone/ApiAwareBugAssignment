import mysql.connector
import pandas as pd
import os.path
from DeepProcess import DeepProcessor
from APIScanner import APIScanner
from CodeScanner import CodeScanner
from Profile import guess_correct_author_name
from base import output_folder
from Results import find_response


# select which project to check
def project_selector():
    import inquirer
    questions = [
        inquirer.List('project',
                      message="Which project should be selected?",
                      choices=['jdt', 'swt', 'birt - not used', 'eclipse_platform_ui - not used'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['project']


# @deprecated : we do not use in-direct any more
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


# select which k-fold formula to use
def formula_selector():
    import inquirer
    questions = [
        inquirer.List('formula',
                      message="Which formula should be used for training-testing?",
                      choices=['similar to BSBA', 'similar to L2R', 'similiar to L2R+'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['formula']


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


# connect to a selected database
def mysql_connection(project_name):
    return mysql.connector.connect(
        host='localhost',
        port='32000',
        user='root',
        password='root',
        database=project_name
    )


# we create the processed_code table within the databases provided by L2R+ work
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
approach = 'direct'  # approach_selector()
formula = formula_selector()

# database work
database = mysql_connection(project)
builder = database.cursor()
make_process_table(builder)

# get all bug reports

builder.execute("""
    SELECT bug_and_files.*, assginee_mapper.assignees,
           assginee_mapper.authors, assginee_mapper.commit_hash, concat(product, '-', component) AS component
    FROM bug_and_files
    JOIN (
            SELECT bug_id, GROUP_CONCAT(assignee) as assignees, GROUP_CONCAT(author) as authors, `commit` as commit_hash, product, component, commit_time
            FROM bug_commit
            group by bug_id
        ) assginee_mapper on assginee_mapper.bug_id = bug_and_files.bug_id
    ORDER BY bug_and_files.report_time
""")

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

# correct the naming mistakes before using it
for index, bug in bugs.iterrows():
    bugs.at[index, 'assignees'] = guess_correct_author_name(bug['assignees'], project)
    bugs.at[index, 'authors'] = guess_correct_author_name(bug['authors'], project)

find_response(bugs, project, approach, formula, builder, scanner)
database.close()
