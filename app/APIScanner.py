# this class is used to find, save, scan and parse APIs and API-related tokens
import mysql.connector
import pandas as pd
import os.path

from mysql.connector import ProgrammingError


class APIScanner:
    def __init__(self):
        # connect to api db
        self.database = mysql.connector.connect(
            host='localhost',
            port='32000',
            user='root',
            password='root',
            database='all_apis'
        )
        self.builder = self.database.cursor()
        # make the table for import-to-jar-mapping
        self.make_table()

    def make_table(self):
        self.builder.execute('''
            create table IF NOT EXISTS import_to_jar
            (
                id int auto_increment,
                importie char(255) null,
                jar char(255) null,
                link text null,
                download_link text null,
                constraint import_to_jar_pk
                    primary key (id)
            );
        ''')

        try:
            self.builder.execute('''
            create index import_to_jar_importie_jar_index on import_to_jar (importie, jar);
            ''')
        except ProgrammingError:
            pass

    def api_preprocess(self, changes, project_name):
        all_imports = set()
        for index_, change in changes.iterrows():
            # change[0] === package
            # strangely, some of the imports required further cleanup
            temp_imports = change[0].replace('"', '').replace(')', '').replace('(', '').replace('\\n', '').split(',')
            for temp_import in temp_imports:
                if temp_import == '':
                    continue
                if temp_import.startswith('.'):
                    continue
                if '.' not in temp_import:
                    continue
                corrected = \
                    temp_import.split('//', 1)[0].split('/*', 1)[0].split('packagepclass', 1)[0].split('classTest', 1)[
                        0].split('publicclass', 1)[0].split('+class', 1)[0].split('{', 1)[0].split('+', 1)[0]
                corrected_imports = corrected.replace('import', '\n').replace('\\r+', '\n')
                corrected_imports_split = corrected_imports.split('\n')

                for s in corrected_imports_split:
                    s = s.lstrip().rstrip().split('\\r', 1)[0]
                    if s.startswith('org.eclipse.' + project_name) or s == '':
                        continue
                    all_imports.add(s)

        exit('1111')
        for each_import in all_imports:
            if each_import.startswith('java'):
                # read the files in Java SE and Java EE
                continue
            # elif :
            # query for it
            # work within the jar file to extract items
            # else:
            # add it to the database
        exit(1)
