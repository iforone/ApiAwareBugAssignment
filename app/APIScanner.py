# this class is used to find, save, scan and parse APIs and API-related tokens
import mysql.connector
import pandas as pd
import os.path

from mysql.connector import ProgrammingError


class APIScanner:
    def __init__(self, with_cleaning):
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
        self.with_cleaning = with_cleaning

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

    def clean_and_process_imports(self, project_name, builder_, db_):
        # get all package in changed files
        builder_.execute("""
            SELECT id, packages, cleaned_packages
            FROM processed_code
            WHERE 1
        """)
        changes = pd.DataFrame(builder_.fetchall())
        all_imports = set()

        if self.with_cleaning == 'yes':
            for index_, change in changes.iterrows():
                all_local_imports = set()
                # change[0] === id
                # change[1] === packages
                # change[2] === cleaned_packages
                # strangely, some of the imports required further cleanup
                temp_imports = change[1].replace('"', '').replace(')', '').replace('(', '').replace('\\n', '').split(',')
                for temp_import in temp_imports:
                    if temp_import == '':
                        continue
                    if temp_import.startswith('.'):
                        continue
                    if '.' not in temp_import:
                        continue
                    corrected = temp_import.split('//', 1)[0].split('/*', 1)[0].split('packagepclass', 1)[0].split('classTest', 1)[0].split('publicclass', 1)[0].split('+class', 1)[0].split('{', 1)[0].split('+', 1)[0]
                    corrected_imports = corrected.replace('import', '\n').replace('\\r+', '\n')
                    corrected_imports_split = corrected_imports.split('\n')

                    for s in corrected_imports_split:
                        s = s.lstrip().rstrip().split('\\r', 1)[0]
                        if s.startswith('org.eclipse.' + project_name) or s == '':
                            continue
                        all_imports.add(s)
                        all_local_imports.add(s)

                cleaned_packages = ','.join(all_local_imports)
                builder_.execute("""update processed_code set cleaned_packages = %s WHERE id = %s """, [cleaned_packages, change[0]])
                db_.commit()
            # fh = open('all_imports_old.txt')
            # ax = [line.rstrip() for line in fh.readlines()]
            # fh.close()
            # f = open("all_imports-6-jan.txt", "a")
            # for elexx in ax:
            #     if elexx in all_imports:
            #         print('✅' + elexx)
            #     else:
            #         print('❓' + elexx)
            #         f.write('NOT FOUND -' + elexx + '\n')
            # f.close()
        else:
            for index_, change in changes.iterrows():
                corrected_imports_split = change[2].split(',')
                for s in corrected_imports_split:
                    all_imports.add(s)

        self.process_imports(all_imports)

    def process_imports(self, all_imports):
        for each_import in all_imports:
            if each_import.startswith('java'):
                # read the files in Java SE and Java EE
                # parse the data and save it to database
                continue
            else:
                self.builder.execute('SELECT jar,link, download_link'
                                     ' FROM import_to_jar WHERE importie = %s', [each_import])
                result = self.builder.fetchone()
                if result is None:
                    link = 'https://www.findjar.com/search?query=' + each_import + '&more=false'
                    download_link = 'https://www.findjar.com/class/' + each_import.replace('.*', '').replace('.', '/') + '.html'
                    self.builder.execute('INSERT INTO import_to_jar (importie, link, download_link) VALUE (%s, %s, %s)', [each_import, link, download_link])
                    self.database.commit()
                    print('⚠️ Warning: source code is using a package we could not track because Jar is not found!')
                    continue
                # work within the jar file to extract items
                exit(each_import)
        exit('OKAY')

