# just base paths and file names or base variables
main_dir = './'
data_folder = 'data'
input_directory = data_folder + '/' + 'input/'
output_folder = data_folder + '/' + 'output/'
tuning_folder = output_folder + 'tuning/'
javase_directory = input_directory + 'javase/'
javaee_directory = input_directory + 'javaee/'
javase_tree_file = 'javase.txt'
javaee_tree_file = 'javaee.txt'
stop_words_file = 'java_stopwords.txt'
SECONDS_IN_A_DAY = 24 * 60 * 60
validation_folder = output_folder + 'validations/'
validation_of_vcs_jdt = validation_folder + 'jdt_vcs_log.txt'

bug_similarity_threshold = 1
bug_api_threshold = 5

ks = [1, 2, 3, 4, 5, 10]

exportable_keys = ['bug_id', 'at_1', 'at_2', 'at_3', 'at_4', 'at_5', 'at_10',
                   'component', 'assignees', 'assignees_copy', 'author', 'chosen', 'extra', 'confidence',
                   # 'similar_bug_report_time',
                   'history_at_1', 'history_at_2', 'history_at_3', 'history_at_4', 'history_at_5', 'history_at_6',
                   'history_at_7', 'history_at_8', 'history_at_9', 'history_at_10',
                   'history_at_1_v', 'history_at_2_v', 'history_at_3_v', 'history_at_4_v', 'history_at_5_v',
                   'history_at_6_v',
                   'history_at_7_v', 'history_at_8_v', 'history_at_9_v', 'history_at_10_v',
                   'code_at_1', 'code_at_2', 'code_at_3', 'code_at_4', 'code_at_5', 'code_at_6', 'code_at_7',
                   'code_at_8',
                   'code_at_9', 'code_at_10',
                   'code_at_1_v', 'code_at_2_v', 'code_at_3_v', 'code_at_4_v', 'code_at_5_v', 'code_at_6_v',
                   'code_at_7_v',
                   'code_at_8_v', 'code_at_9_v', 'code_at_10_v',
                   'api_at_1', 'api_at_2', 'api_at_3', 'api_at_4', 'api_at_5', 'api_at_6', 'api_at_7', 'api_at_8',
                   'api_at_9',
                   'api_at_10',
                   'api_at_1_v', 'api_at_2_v', 'api_at_3_v', 'api_at_4_v', 'api_at_5_v', 'api_at_6_v', 'api_at_7_v',
                   'api_at_8_v', 'api_at_9_v', 'api_at_10_v', 'report_time'
                   ]

jdt_fixable_names = {
    # in JDT
    'cknaus': 'Claude Knaus',
    'Andrew Weinand': 'Andre Weinand',
    'Thomas Maeder': 'Thomas M??der',
    'tbay': 'Till Bay',
    'Kai Maetzel': 'Kai-Uwe Maetzel',
    'dspringgay': 'Grant Gayed',
    'mhuebscher': 'Markus Huebscher',
    'jszurszewski': 'Joe Szurszewski',
    'teicher': 'Tom Hofmann',
    'Tom Eicher': 'Tom Hoffmann',
    # https://projects.eclipse.org/content/tom-hofmann-nee-eicher-committer-ui

    # in SWT:
    'Arun Kumar Thondapu': 'Arun Thondapu',
    'ggayed': 'Grant Gayed',
    'y29cheng': 'George Cheng',
    'steve': 'Steve Northover',
    'Silenio': 'Silenio Quarti',
    'rdowdall': 'Rodney Dowdall',
    'Lynn Kues': 'Lynne Kues',
    'Anatoly Spektor': 'Arun Thondapu',
    'Praveen Innamuri': 'Praveen',
    'SWT-Community-Hudson-Inbox': 'Community-Hudson',
}

# modes
LEARN = 'LEARN'
TEST = 'TEST'
