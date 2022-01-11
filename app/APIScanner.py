# this class is used to find, save, scan and parse APIs and API-related tokens
import re
import mysql.connector
import pandas as pd
import subprocess

from mysql.connector import ProgrammingError


def run_java(c):
    command = "docker exec -i my_little_alpine bash -c \"" + c + "\""
    process = subprocess.run(command, capture_output=True, shell=True)
    return process.stdout.decode("utf-8")


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
        self.make_api_table()
        self.make_scanner_table()
        self.with_cleaning = with_cleaning

    def make_scanner_table(self):
        self.builder.execute('''
            create table IF NOT EXISTS scans
            (
                id int auto_increment,
                importie char(255) null,
                jar char(255) null,
                api char(255) null,
                classifiers text null,
                methods text null,
                constants text null,
                full_resolution longtext null,
                constraint scans_pk
                    primary key (id)
            );
        ''')

    def make_api_table(self):
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
                temp_imports = change[1].replace('"', '').replace(')', '').replace('(', '').replace('\\n', '').split(
                    ',')
                for temp_import in temp_imports:
                    if temp_import == '':
                        continue
                    if temp_import.startswith('.'):
                        continue
                    if '.' not in temp_import:
                        continue
                    corrected = \
                        temp_import.split('//', 1)[0].split('/*', 1)[0].split('packagepclass', 1)[0].split('classTest',
                                                                                                           1)[
                            0].split('publicclass', 1)[0].split('+class', 1)[0].split('{', 1)[0].split('+', 1)[0]
                    corrected_imports = corrected.replace('import', '\n').replace('\\r+', '\n')
                    corrected_imports_split = corrected_imports.split('\n')

                    for s in corrected_imports_split:
                        s = s.lstrip().rstrip().split('\\r', 1)[0]
                        if s.startswith('org.eclipse.' + project_name) or s == '':
                            continue
                        all_imports.add(s)
                        all_local_imports.add(s)

                cleaned_packages = ','.join(all_local_imports)
                builder_.execute("""update processed_code set cleaned_packages = %s WHERE id = %s """,
                                 [cleaned_packages, change[0]])
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

        f = open("all-imports.txt", "a")
        for i in all_imports:
            f.write(i + '\n')
        f.close()

        self.process_imports(all_imports)

    def process_imports(self, all_imports):
        for each_import in all_imports:
            if each_import == '':
                continue
            if each_import.startswith('java'):
                # read the files in Java SE and Java EE
                # parse the data and save it to database
                continue
            else:
                self.builder.execute('SELECT jar'
                                     ' FROM import_to_jar WHERE importie = %s', [each_import])
                result = self.builder.fetchone()
                if result is None:
                    link = 'https://www.findjar.com/search?query=' + each_import + '&more=false'
                    download_link = 'https://www.findjar.com/class/' + each_import.replace('.*', '').replace('.',
                                                                                                             '/') + '.html'
                    self.builder.execute('INSERT INTO import_to_jar (importie, link, download_link) VALUE (%s, %s, %s)',
                                         [each_import, link, download_link])
                    self.database.commit()
                    print('⚠️ Warning: source code is using a package we could not track because Jar is not found!')
                    continue
                # work within the jar file to extract items
                self.scan_jar(each_import, result[0])
        exit('OKAY')

    # how to just get constants -> just run constants and look for Enum or final
    # 1- ✅ Classifier - class or interface or EnumType (like a type of enum)
    # 2- ✅ Methods method names
    # 3- ✅ Enum constants - constants or constant values of an enum
    def scan_jar(self, importie, jar=None):
        if jar is None:
            return
        if jar == 'none':
            return
        if importie.endswith('.*'):
            return
            # we need this because of the wildcard or star imports
            # this might be useful for all scenarios
            package = importie.replace('.*', '').replace('.', '/')
            answer = run_java('cd input/jars && jar -tf "' + jar + '" ' + package)
            relevant_packages = answer.split('\n')

            for relevant_package in relevant_packages:
                relevant_importie = relevant_package.replace('/', '.').replace('$', '.')
                print('so -*' + relevant_package + '*\n')
            return

        # normal imports:
        classifiers = set()
        methods = set()
        constants = set()
        try:
            relevant_importie = importie
            # check whether the public is sufficient
            all_class_text = run_java('cd input/jars && javap -public -cp "' + jar + '" ' + relevant_importie).rstrip()
            class_lines = all_class_text.split('\n')

            class_name_not_good = class_lines[1]
            class_index = class_name_not_good.find('class')
            if class_index != -1:
                class_name = class_name_not_good[class_index + 5:].lstrip().split()[0].rstrip().lstrip()
            else:
                class_name = class_name_not_good[class_name_not_good.find('interface') + 9:].lstrip().split()[
                    0].rstrip().lstrip()

            classifiers.add(class_name)
            classifiers.add(class_name.replace('$', '.'))
            classifiers.add(class_name.split('.')[-1].replace('$', '.'))
            classifiers.add(class_name.replace('$', '.').split('.')[-1])
            # this is the constructor method - if not already there
            methods.add(class_name.replace('$', '.').split('.')[-1])

            for class_line in class_lines[2:]:
                class_line = class_line.lstrip()
                # is method
                if '(' in class_line:
                    method_ = class_line.split('(')[0].split(' ')[-1]

                    methods.add(method_)
                    # print('method: ' + method_)
                # is enum
                elif 'final ' + class_name in class_line:
                    enum_type = class_name
                    const_ = class_line.split(' ')[-1][:-1]

                    constants.add(enum_type.split('.')[-1].replace('$', '.') + '.' + const_)
                    constants.add(enum_type.replace('$', '.').split('.')[-1] + '.' + const_)
                    constants.add(const_)
                    # print('enum of' + enum_type + '--' + const_)
                # is constant
                elif 'final ' in class_line and class_line.endswith(
                        ';') and '{' not in class_line and '}' not in class_line:
                    const_ = class_line.split(' ')[-1][:-1]

                    constants.add(const_)
                    # print('constant: ' + const_)

            self.builder.execute(
                'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution)'
                ' VALUE (%s, %s, %s, %s, %s, %s, %s)',
                [importie, jar, '', ','.join(classifiers), ','.join(methods), ','.join(constants), all_class_text])
            self.database.commit()
        except:
            print('this failed unfortunately')
            print('cd input/jars && javap -public -cp "' + jar + '" ' + importie)
        # tokenize
        # check against the code
        # add to used_api
        pass
