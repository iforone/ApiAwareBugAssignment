import mysql.connector
import pandas as pd

# select which project to check
def project_selector():
    import inquirer
    questions = [
        inquirer.List('project',
                      message="What size do you need?",
                      choices=['jdt', 'swt', 'birt', 'eclipse_platform_ui'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers['project']


# connect to a selected database
def mysql_connection(project_name):
    return mysql.connector.connect(
        host='localhost',
        port='32000',
        user='root',
        password='root',
        database=project_name
    )


print('Running Python')

project = project_selector()
database = mysql_connection(project)

# get all bugs
builder = database.cursor()
builder.execute("SELECT * FROM bug_and_files ORDER BY report_time")
result = pd.DataFrame(builder.fetchall())
result.columns = builder.column_names

# loop through each bug
for index, row in result.iterrows():
    print(row['bug_id'])

database.close()
